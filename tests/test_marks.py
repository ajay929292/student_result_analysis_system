import io
import pytest
import pandas as pd
from app import create_app, db
from app.models import User, AcademicYear, Class, Subject, ClassSubject, Student, ExamTerm, Marks, GradingScale, GradeRule
from app.services.grading_service import GradingService
from app.services.ingestion_service import MarksIngestionService


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

        # Seed Grading Scale
        scale = GradingScale(scale_name="IGNOU Standard 10-Point", is_active=True)
        db.session.add_all([admin, teacher, student_user, scale])
        db.session.flush()

        rules_data = [
            (85.0, 100.0, 'O', 10.0, 'Outstanding'),
            (75.0, 84.99, 'A+', 9.0, 'Excellent'),
            (65.0, 74.99, 'A', 8.0, 'Very Good'),
            (55.0, 64.99, 'B+', 7.0, 'Good'),
            (50.0, 54.99, 'B', 6.0, 'Above Average'),
            (40.0, 49.99, 'C', 5.0, 'Average'),
            (0.0, 39.99, 'F', 0.0, 'Fail')
        ]
        for r in rules_data:
            db.session.add(GradeRule(
                scale_id=scale.scale_id,
                min_percentage=r[0],
                max_percentage=r[1],
                grade_letter=r[2],
                grade_point=r[3],
                description=r[4]
            ))

        # Seed Academic Year, Class, Subject, Curriculum Mapping
        year = AcademicYear(year_label='2025-2026', is_active=True)
        db.session.add(year)
        db.session.flush()

        cls = Class(class_name='BCA-Sem-1', section='A', year_id=year.year_id)
        sub = Subject(subject_code='BCS-011', subject_name='Computer Basics', credits=3)
        term = ExamTerm(term_name='TEE June 2025', year_id=year.year_id, is_locked=False)
        db.session.add_all([cls, sub, term])
        db.session.flush()

        mapping = ClassSubject(
            class_id=cls.class_id,
            subject_id=sub.subject_id,
            max_internal_marks=30.0,
            max_external_marks=70.0,
            pass_marks=40.0
        )
        db.session.add(mapping)
        db.session.flush()

        # Seed 2 Students
        st1 = Student(enrollment_no='240100101', full_name='Aarav Sharma', class_id=cls.class_id)
        st2 = Student(enrollment_no='240100102', full_name='Diya Patel', class_id=cls.class_id)
        db.session.add_all([st1, st2])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username='teacher', password='Teacher@123'):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


# --------------------------------------------------------------------------
# 1. GradingService Unit Tests
# --------------------------------------------------------------------------
def test_grading_service_evaluation(app):
    """Test percentage calculation, pass criteria, and grade mapping."""
    with app.app_context():
        # Outstanding (O): 28/30 internal + 60/70 external = 88/100 -> 88.0%
        res_o = GradingService.evaluate(28.0, 60.0, 30.0, 70.0, 40.0)
        assert res_o['total_marks'] == 88.0
        assert res_o['percentage'] == 88.0
        assert res_o['is_passed'] is True
        assert res_o['grade'] == 'O'
        assert res_o['grade_point'] == 10.0

        # Excellent (A+): 22/30 + 55/70 = 77/100 -> 77.0%
        res_ap = GradingService.evaluate(22.0, 55.0, 30.0, 70.0, 40.0)
        assert res_ap['grade'] == 'A+'
        assert res_ap['grade_point'] == 9.0

        # Average (C): 12/30 + 30/70 = 42/100 -> 42.0%
        res_c = GradingService.evaluate(12.0, 30.0, 30.0, 70.0, 40.0)
        assert res_c['grade'] == 'C'
        assert res_c['is_passed'] is True

        # Failed (F): 10/30 + 20/70 = 30/100 -> 30.0% (< 40 pass mark)
        res_f = GradingService.evaluate(10.0, 20.0, 30.0, 70.0, 40.0)
        assert res_f['is_passed'] is False
        assert res_f['grade'] == 'F'
        assert res_f['grade_point'] == 0.0

        # Absent
        res_ab = GradingService.evaluate(25.0, 60.0, 30.0, 70.0, 40.0, is_absent=True)
        assert res_ab['total_marks'] == 0.0
        assert res_ab['percentage'] == 0.0
        assert res_ab['is_absent'] is True
        assert res_ab['is_passed'] is False
        assert res_ab['grade'] == 'F'


# --------------------------------------------------------------------------
# 2. Interactive Manual Marks Entry Tests
# --------------------------------------------------------------------------
def test_marks_entry_page_access_and_filter(client):
    """Test accessing marks entry grid with class, subject, and term parameters."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        term = ExamTerm.query.first()
        c_id, s_id, t_id = cls.class_id, sub.subject_id, term.term_id

    res = client.get(f'/marks/entry?class_id={c_id}&subject_id={s_id}&term_id={t_id}')
    assert res.status_code == 200
    assert b'Enrolled Student Score Registry' in res.data
    assert b'240100101' in res.data
    assert b'240100102' in res.data


def test_save_manual_marks_batch(client):
    """Test batch saving manual marks and verifying calculation and audit user."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        term = ExamTerm.query.first()
        st1 = Student.query.filter_by(enrollment_no='240100101').first()
        st2 = Student.query.filter_by(enrollment_no='240100102').first()
        c_id, s_id, t_id = cls.class_id, sub.subject_id, term.term_id
        st1_id, st2_id = st1.student_id, st2.student_id

    # Post scores: st1 scored 25 internal / 60 external, st2 is absent
    post_data = {
        'class_id': c_id,
        'subject_id': s_id,
        'term_id': t_id,
        'student_ids': [st1_id, st2_id],
        f'internal_{st1_id}': '25.0',
        f'external_{st1_id}': '60.0',
        f'internal_{st2_id}': '0.0',
        f'external_{st2_id}': '0.0',
        f'absent_{st2_id}': '1'
    }

    res = client.post('/marks/entry', data=post_data, follow_redirects=True)
    assert res.status_code == 200
    assert b'Successfully evaluated and recorded marks' in res.data

    with client.application.app_context():
        mapping = ClassSubject.query.filter_by(class_id=c_id, subject_id=s_id).first()

        # Check st1 marks
        mk1 = Marks.query.filter_by(student_id=st1_id, class_subject_id=mapping.class_subject_id, term_id=t_id).first()
        assert mk1 is not None
        assert mk1.total_marks == 85.0
        assert mk1.percentage == 85.0
        assert mk1.grade == 'O'
        assert mk1.grade_point == 10.0
        assert mk1.is_passed is True
        assert mk1.is_absent is False
        assert mk1.updated_by is not None

        # Check st2 absent marks
        mk2 = Marks.query.filter_by(student_id=st2_id, class_subject_id=mapping.class_subject_id, term_id=t_id).first()
        assert mk2 is not None
        assert mk2.total_marks == 0.0
        assert mk2.is_absent is True
        assert mk2.grade == 'F'
        assert mk2.is_passed is False


# --------------------------------------------------------------------------
# 3. Exam Term Locking Tests
# --------------------------------------------------------------------------
def test_term_locking_prevents_marks_modification(client):
    """Test that locked exam term prevents marks modification."""
    # First login as admin to lock the term
    login(client, 'admin', 'Admin@123')

    with client.application.app_context():
        term = ExamTerm.query.first()
        term_id = term.term_id

    # Toggle lock on
    res = client.post(f'/marks/terms/{term_id}/toggle-lock', follow_redirects=True)
    assert res.status_code == 200
    assert b'LOCKED' in res.data

    with client.application.app_context():
        t = db.session.get(ExamTerm, term_id)
        assert t.is_locked is True

    # Attempt to post marks to locked term should be rejected
    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        st1 = Student.query.first()
        c_id, s_id, st1_id = cls.class_id, sub.subject_id, st1.student_id

    res = client.post('/marks/entry', data={
        'class_id': c_id,
        'subject_id': s_id,
        'term_id': term_id,
        'student_ids': [st1_id],
        f'internal_{st1_id}': '20.0',
        f'external_{st1_id}': '50.0'
    }, follow_redirects=True)

    assert b'locked. Modification is forbidden' in res.data


# --------------------------------------------------------------------------
# 4. Batch CSV & Excel Ingestion with Atomic Rollback Tests
# --------------------------------------------------------------------------
def test_batch_csv_ingestion_success(client):
    """Test valid bulk CSV marks ingestion with automated calculations."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        term = ExamTerm.query.first()
        c_id, s_id, t_id = cls.class_id, sub.subject_id, term.term_id

    csv_data = (
        "enrollment_no,internal_marks,external_marks,is_absent\n"
        "240100101,26.0,52.0,0\n"
        "240100102,18.0,45.0,0\n"
    )

    data = {
        'class_id': str(c_id),
        'subject_id': str(s_id),
        'term_id': str(t_id),
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'test_marks.csv')
    }

    res = client.post('/marks/bulk-upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b'Successfully ingested 2 student marks' in res.data

    with client.application.app_context():
        mapping = ClassSubject.query.filter_by(class_id=c_id, subject_id=s_id).first()
        st1 = Student.query.filter_by(enrollment_no='240100101').first()
        m1 = Marks.query.filter_by(student_id=st1.student_id, class_subject_id=mapping.class_subject_id).first()
        assert m1 is not None
        assert m1.total_marks == 78.0
        assert m1.grade == 'A+'
        assert m1.is_passed is True


def test_batch_excel_ingestion_success(client):
    """Test valid bulk Excel (.xlsx) marks ingestion with automated calculations."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        term = ExamTerm.query.first()
        c_id, s_id, t_id = cls.class_id, sub.subject_id, term.term_id

    df = pd.DataFrame([
        {'enrollment_no': '240100101', 'internal_marks': 22.5, 'external_marks': 48.0, 'is_absent': 0},
        {'enrollment_no': '240100102', 'internal_marks': 0.0, 'external_marks': 0.0, 'is_absent': 1}
    ])
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_buffer.seek(0)

    data = {
        'class_id': str(c_id),
        'subject_id': str(s_id),
        'term_id': str(t_id),
        'file': (excel_buffer, 'test_marks.xlsx')
    }

    res = client.post('/marks/bulk-upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    assert res.status_code == 200
    assert b'Successfully ingested 2 student marks' in res.data

    with client.application.app_context():
        mapping = ClassSubject.query.filter_by(class_id=c_id, subject_id=s_id).first()
        st2 = Student.query.filter_by(enrollment_no='240100102').first()
        m2 = Marks.query.filter_by(student_id=st2.student_id, class_subject_id=mapping.class_subject_id).first()
        assert m2 is not None
        assert m2.is_absent is True
        assert m2.grade == 'F'


def test_batch_ingestion_atomic_rollback_on_out_of_range(client):
    """Test atomic rollback: if internal marks exceed max (30), entire batch is rejected."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        term = ExamTerm.query.first()
        c_id, s_id, t_id = cls.class_id, sub.subject_id, term.term_id

    # 240100102 has internal marks 35.0 which exceeds max (30.0)
    csv_data = (
        "enrollment_no,internal_marks,external_marks\n"
        "240100101,25.0,55.0\n"
        "240100102,35.0,50.0\n"
    )

    data = {
        'class_id': str(c_id),
        'subject_id': str(s_id),
        'term_id': str(t_id),
        'file': (io.BytesIO(csv_data.encode('utf-8')), 'invalid_marks.csv')
    }

    res = client.post('/marks/bulk-upload', data=data, content_type='multipart/form-data')
    assert res.status_code == 200
    assert b'Spreadsheet Ingestion Rejected' in res.data
    assert b'must be between 0 and maximum (30.0)' in res.data

    # Verify zero records committed
    with client.application.app_context():
        mapping = ClassSubject.query.filter_by(class_id=c_id, subject_id=s_id).first()
        st1 = Student.query.filter_by(enrollment_no='240100101').first()
        assert Marks.query.filter_by(student_id=st1.student_id, class_subject_id=mapping.class_subject_id).first() is None


# --------------------------------------------------------------------------
# 5. Template Generation Tests
# --------------------------------------------------------------------------
def test_download_marks_template_csv_and_excel(client):
    """Test downloading pre-populated CSV and Excel evaluation templates."""
    login(client, 'teacher', 'Teacher@123')

    with client.application.app_context():
        cls = Class.query.first()
        sub = Subject.query.first()
        c_id, s_id = cls.class_id, sub.subject_id

    # CSV template
    res_csv = client.get(f'/marks/template?class_id={c_id}&subject_id={s_id}&format=csv')
    assert res_csv.status_code == 200
    assert res_csv.headers['Content-Type'] == 'text/csv; charset=utf-8'
    assert b'enrollment_no,student_name,internal_marks,external_marks,is_absent' in res_csv.data
    assert b'240100101' in res_csv.data

    # Excel template
    res_xlsx = client.get(f'/marks/template?class_id={c_id}&subject_id={s_id}&format=xlsx')
    assert res_xlsx.status_code == 200
    assert 'spreadsheetml.sheet' in res_xlsx.headers['Content-Type']
    assert len(res_xlsx.data) > 1000  # Valid binary Excel payload
