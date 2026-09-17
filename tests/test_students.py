import io
import pytest
from app import create_app, db
from app.models import User, AcademicYear, Class, Student


@pytest.fixture
def app():
    """Create test application configured with an in-memory database."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()

        # Seed users
        admin = User(username='admin', full_name='Admin User', role=User.ROLE_ADMIN)
        admin.set_password('Admin@123')

        teacher = User(username='teacher', full_name='Teacher User', role=User.ROLE_TEACHER)
        teacher.set_password('Teacher@123')

        student_user = User(username='student', full_name='Student User', role=User.ROLE_STUDENT)
        student_user.set_password('Student@123')

        # Seed academic year & class
        year = AcademicYear(year_label='2025-2026', is_active=True)
        db.session.add_all([admin, teacher, student_user, year])
        db.session.commit()

        cls1 = Class(class_name='BCA-Sem-1', section='A', year_id=year.year_id)
        cls2 = Class(class_name='BCA-Sem-2', section='A', year_id=year.year_id)
        db.session.add_all([cls1, cls2])
        db.session.commit()

        # Seed a student
        st1 = Student(enrollment_no='240100101', full_name='Aarav Sharma', email='aarav@ignou.ac.in', class_id=cls1.class_id)
        db.session.add(st1)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username='teacher', password='Teacher@123'):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


def test_student_roster_access(client):
    """Test that student roster is protected and accessible by teachers/admins."""
    # Unauthenticated
    res = client.get('/students/')
    assert res.status_code == 302
    assert '/login' in res.headers['Location']

    # Log in as teacher
    login(client, 'teacher', 'Teacher@123')
    res = client.get('/students/')
    assert res.status_code == 200
    assert b'Student Enrollment Roster' in res.data
    assert b'240100101' in res.data


def test_single_student_registration(client):
    """Test registering a new individual student."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        cls_id = cls.class_id

    # Create new student
    res = client.post('/students/new', data={
        'enrollment_no': '240100102',
        'full_name': 'Priya Singh',
        'email': 'priya@ignou.ac.in',
        'class_id': cls_id
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'successfully enrolled' in res.data

    with client.application.app_context():
        st = Student.query.filter_by(enrollment_no='240100102').first()
        assert st is not None
        assert st.full_name == 'Priya Singh'


def test_duplicate_enrollment_rejection(client):
    """Test that registering an already existing enrollment number is rejected."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        cls_id = cls.class_id

    # Try duplicate enrollment
    res = client.post('/students/new', data={
        'enrollment_no': '240100101',  # already seeded
        'full_name': 'Duplicate Person',
        'email': 'dup@ignou.ac.in',
        'class_id': cls_id
    }, follow_redirects=True)
    assert b'already registered' in res.data


def test_edit_student(client):
    """Test editing an existing student profile."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        st = Student.query.filter_by(enrollment_no='240100101').first()
        st_id = st.student_id
        cls2 = Class.query.filter_by(class_name='BCA-Sem-2').first()
        cls2_id = cls2.class_id

    res = client.post(f'/students/edit/{st_id}', data={
        'full_name': 'Aarav Sharma Updated',
        'email': 'aarav.updated@ignou.ac.in',
        'class_id': cls2_id
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'updated' in res.data

    with client.application.app_context():
        st = db.session.get(Student, st_id)
        assert st.full_name == 'Aarav Sharma Updated'
        assert st.email == 'aarav.updated@ignou.ac.in'
        assert st.class_id == cls2_id


def test_delete_student(client):
    """Test removing a student profile (admin only)."""
    # Teacher cannot delete
    login(client, 'teacher', 'Teacher@123')
    with client.application.app_context():
        st = Student.query.filter_by(enrollment_no='240100101').first()
        st_id = st.student_id

    res = client.post(f'/students/delete/{st_id}', follow_redirects=True)
    assert b'Access denied' in res.data

    # Admin can delete
    client.get('/logout')
    login(client, 'admin', 'Admin@123')
    res = client.post(f'/students/delete/{st_id}', follow_redirects=True)
    assert res.status_code == 200
    assert b'removed from system records' in res.data

    with client.application.app_context():
        assert db.session.get(Student, st_id) is None


def test_student_search_and_filter(client):
    """Test searching by query string and filtering by class."""
    login(client, 'teacher', 'Teacher@123')

    # Search for Aarav
    res = client.get('/students/?q=Aarav')
    assert b'240100101' in res.data

    # Search non-existent
    res = client.get('/students/?q=NonExistentPerson')
    assert b'No students found' in res.data


def test_batch_csv_upload_success(client):
    """Test valid CSV bulk enrollment."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        cls_id = cls.class_id

    csv_data = (
        "enrollment_no,full_name,email\n"
        "240100201,Rohit Mehta,rohit@ignou.ac.in\n"
        "240100202,Kavita Nair,kavita@ignou.ac.in\n"
        "240100203,Deepak Kumar,deepak@ignou.ac.in\n"
    )

    data = {
        'class_id': str(cls_id),
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'students.csv')
    }

    res = client.post('/students/bulk-upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b'Successfully enrolled 3 students' in res.data

    with client.application.app_context():
        st = Student.query.filter_by(enrollment_no='240100201').first()
        assert st is not None
        assert st.full_name == 'Rohit Mehta'


def test_batch_csv_atomic_rollback_on_duplicate(client):
    """Test atomic rollback: if one row contains duplicate, entire batch is rejected."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        cls_id = cls.class_id

    # 240100101 already exists in DB
    csv_data = (
        "enrollment_no,full_name,email\n"
        "240100301,Valid Student One,v1@ignou.ac.in\n"
        "240100101,Preexisting Duplicate,dup@ignou.ac.in\n"
        "240100302,Valid Student Two,v2@ignou.ac.in\n"
    )

    data = {
        'class_id': str(cls_id),
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'test_batch.csv')
    }

    res = client.post('/students/bulk-upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    assert b'Batch Upload Rejected' in res.data
    assert b'already registered' in res.data

    # Verify zero records from this batch were inserted (atomic principle)
    with client.application.app_context():
        assert Student.query.filter_by(enrollment_no='240100301').first() is None
        assert Student.query.filter_by(enrollment_no='240100302').first() is None


def test_download_template_csv(client):
    """Test downloading the student enrollment CSV template."""
    login(client, 'teacher', 'Teacher@123')

    res = client.get('/students/template.csv')
    assert res.status_code == 200
    assert res.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert b'enrollment_no,full_name,email' in res.data
