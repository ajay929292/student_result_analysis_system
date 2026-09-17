import pytest
from app import create_app, db
from app.models import User, AcademicYear, Class, Subject, ClassSubject


@pytest.fixture
def app():
    """Create test application configured with an in-memory database."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        # Seed admin, teacher, student
        admin = User(username='admin', full_name='Admin User', role=User.ROLE_ADMIN)
        admin.set_password('Admin@123')

        teacher = User(username='teacher', full_name='Teacher User', role=User.ROLE_TEACHER)
        teacher.set_password('Teacher@123')

        student = User(username='student', full_name='Student User', role=User.ROLE_STUDENT)
        student.set_password('Student@123')

        # Seed base academic data
        year = AcademicYear(year_label='2025-2026', is_active=True)
        db.session.add_all([admin, teacher, student, year])
        db.session.commit()

        cls = Class(class_name='BCA-Sem-1', section='A', year_id=year.year_id)
        sub = Subject(subject_code='BCS-011', subject_name='Computer Basics', credits=3)
        db.session.add_all([cls, sub])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username='admin', password='Admin@123'):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_academic_index_access(client):
    """Test academic management hub requires teacher or admin login."""
    # Unauthenticated should redirect
    res = client.get('/academic/')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

    # Student should be denied
    login(client, 'student', 'Student@123')
    res = client.get('/academic/', follow_redirects=True)
    assert b'Access denied' in res.data

    # Teacher should succeed
    client.get('/logout')
    login(client, 'teacher', 'Teacher@123')
    res = client.get('/academic/')
    assert res.status_code == 200
    assert b'Academic Setup & Registry' in res.data


def test_create_academic_year(client):
    """Test creating an academic year and toggling active status."""
    login(client, 'admin', 'Admin@123')

    # Create new year
    res = client.post('/academic/years', data={
        'year_label': '2026-2027',
        'is_active': '1'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'created successfully' in res.data

    with client.application.app_context():
        y = AcademicYear.query.filter_by(year_label='2026-2027').first()
        assert y is not None
        assert y.is_active is True

        # Old year should now be inactive
        old_y = AcademicYear.query.filter_by(year_label='2025-2026').first()
        assert old_y.is_active is False

    # Test duplicate year label rejection
    res = client.post('/academic/years', data={
        'year_label': '2026-2027'
    }, follow_redirects=True)
    assert b'already exists' in res.data


def test_toggle_year_active(client):
    """Test explicitly setting an academic year as the active session."""
    login(client, 'admin', 'Admin@123')

    # Add second year inactive
    client.post('/academic/years', data={'year_label': '2027-2028'}, follow_redirects=True)

    with client.application.app_context():
        y2027 = AcademicYear.query.filter_by(year_label='2027-2028').first()
        assert y2027.is_active is False
        y2027_id = y2027.year_id

    # Toggle it active
    res = client.post(f'/academic/years/{y2027_id}/toggle-active', follow_redirects=True)
    assert res.status_code == 200
    assert b'active session' in res.data

    with client.application.app_context():
        y2027 = db.session.get(AcademicYear, y2027_id)
        assert y2027.is_active is True
        y2025 = AcademicYear.query.filter_by(year_label='2025-2026').first()
        assert y2025.is_active is False


def test_create_and_delete_class(client):
    """Test creating a class and deleting an empty class."""
    login(client, 'admin', 'Admin@123')

    with client.application.app_context():
        year = AcademicYear.query.filter_by(year_label='2025-2026').first()
        year_id = year.year_id

    # Create new class
    res = client.post('/academic/classes', data={
        'class_name': 'MCA-Sem-1',
        'section': 'B',
        'year_id': year_id
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'created successfully' in res.data

    with client.application.app_context():
        cls = Class.query.filter_by(class_name='MCA-Sem-1', section='B').first()
        assert cls is not None
        cls_id = cls.class_id

    # Delete empty class
    res = client.post(f'/academic/classes/{cls_id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert b'deleted successfully' in res.data

    with client.application.app_context():
        assert db.session.get(Class, cls_id) is None


def test_create_subject(client):
    """Test registering a subject in the master registry."""
    login(client, 'admin', 'Admin@123')

    res = client.post('/academic/subjects', data={
        'subject_code': 'MCS-211',
        'subject_name': 'Design and Analysis of Algorithms',
        'credits': 4
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'added to registry' in res.data

    with client.application.app_context():
        s = Subject.query.filter_by(subject_code='MCS-211').first()
        assert s is not None
        assert s.credits == 4

    # Duplicate code rejection
    res = client.post('/academic/subjects', data={
        'subject_code': 'MCS-211',
        'subject_name': 'Duplicate Code',
        'credits': 4
    }, follow_redirects=True)
    assert b'already registered' in res.data


def test_curriculum_mapping_flow(client):
    """Test mapping a subject to a class and deleting mapping."""
    login(client, 'admin', 'Admin@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        cls_id = cls.class_id
        sub_id = sub.subject_id

    # Map subject to class
    res = client.post('/academic/curriculum', data={
        'class_id': cls_id,
        'subject_id': sub_id,
        'max_internal_marks': 30,
        'max_external_marks': 70,
        'pass_marks': 40
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Subject successfully mapped' in res.data

    with client.application.app_context():
        mapping = ClassSubject.query.filter_by(class_id=cls_id, subject_id=sub_id).first()
        assert mapping is not None
        assert mapping.max_internal_marks == 30.0
        mapping_id = mapping.mapping_id

    # Delete mapping
    res = client.post(f'/academic/curriculum/{mapping_id}/delete', follow_redirects=True)
    assert res.status_code == 200
    assert b'Curriculum course association removed' in res.data

    with client.application.app_context():
        assert db.session.get(ClassSubject, mapping_id) is None
