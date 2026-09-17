import pytest
from app import create_app, db
from app.models import (
    User, AcademicYear, Class, Subject, ClassSubject,
    Student, ExamTerm, GradingScale, GradeRule, Marks
)


@pytest.fixture
def app():
    """Create test application configured with an in-memory SQLite database."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_user_password_hashing(app):
    """Test user password hashing and verification with bcrypt."""
    user = User(username='testadmin', full_name='Test Admin', role=User.ROLE_ADMIN)
    user.set_password('Secret@123')

    assert user.password_hash != 'Secret@123'
    assert user.check_password('Secret@123') is True
    assert user.check_password('WrongPass') is False
    assert user.is_admin is True
    assert user.is_teacher is True

    # Empty password check
    with pytest.raises(ValueError):
        user.set_password('')


def test_academic_and_class_models(app):
    """Test AcademicYear, Class, Subject, and ClassSubject mappings."""
    ay = AcademicYear(year_label='2025-2026', is_active=True)
    db.session.add(ay)
    db.session.flush()

    cls = Class(class_name='BCA-Semester-1', section='A', year_id=ay.year_id)
    db.session.add(cls)
    db.session.flush()

    subj = Subject(subject_code='BCS-011', subject_name='Computer Basics', credits=3)
    db.session.add(subj)
    db.session.flush()

    mapping = ClassSubject(
        class_id=cls.class_id,
        subject_id=subj.subject_id,
        max_internal_marks=30.0,
        max_external_marks=70.0,
        pass_marks=40.0
    )
    db.session.add(mapping)
    db.session.commit()

    assert mapping.max_total_marks == 100.0
    assert cls.display_name == "BCA-Semester-1 - Sec A"
    assert len(cls.class_subjects) == 1
    assert cls.class_subjects[0].subject_ref.subject_code == 'BCS-011'


def test_student_and_marks_calculation(app):
    """Test Student profile, ExamTerm, and automated marks calculation."""
    ay = AcademicYear(year_label='2025-2026', is_active=True)
    db.session.add(ay)
    db.session.flush()

    cls = Class(class_name='BCA-Semester-1', section='A', year_id=ay.year_id)
    db.session.add(cls)
    db.session.flush()

    subj = Subject(subject_code='BCS-011', subject_name='Computer Basics', credits=3)
    db.session.add(subj)
    db.session.flush()

    mapping = ClassSubject(
        class_id=cls.class_id,
        subject_id=subj.subject_id,
        max_internal_marks=30.0,
        max_external_marks=70.0,
        pass_marks=40.0
    )
    db.session.add(mapping)
    db.session.flush()

    student = Student(enrollment_no='230100999', full_name='John Doe', class_id=cls.class_id)
    term = ExamTerm(term_name='TEE June 2025', year_id=ay.year_id)
    db.session.add_all([student, term])
    db.session.commit()

    # Normal passing mark
    mark1 = Marks(
        student_id=student.student_id,
        class_subject_id=mapping.class_subject_id,
        term_id=term.term_id,
        internal_marks=24.0,
        external_marks=56.0
    )
    db.session.add(mark1)
    mark1.calculate()
    db.session.commit()

    assert mark1.total_marks == 80.0
    assert mark1.percentage == 80.0
    assert mark1.is_passed is True

    # Absent student mark
    student2 = Student(enrollment_no='230100998', full_name='Jane Doe', class_id=cls.class_id)
    db.session.add(student2)
    db.session.commit()

    mark2 = Marks(
        student_id=student2.student_id,
        class_subject_id=mapping.class_subject_id,
        term_id=term.term_id,
        internal_marks=20.0,
        external_marks=50.0,
        is_absent=True
    )
    mark2.calculate()
    assert mark2.total_marks == 0.0
    assert mark2.grade == 'F'
    assert mark2.is_passed is False


def test_grading_scale_rules(app):
    """Test dynamic grading scale rules hierarchy."""
    scale = GradingScale(scale_name='IGNOU Standard 10-Point', is_active=True)
    db.session.add(scale)
    db.session.flush()

    rule_o = GradeRule(
        scale_id=scale.scale_id,
        min_percentage=85.0,
        max_percentage=100.0,
        grade_letter='O',
        grade_point=10.0,
        description='Outstanding'
    )
    rule_f = GradeRule(
        scale_id=scale.scale_id,
        min_percentage=0.0,
        max_percentage=39.99,
        grade_letter='F',
        grade_point=0.0,
        description='Fail'
    )
    db.session.add_all([rule_o, rule_f])
    db.session.commit()

    assert len(scale.rules) == 2
    # Ordered by min_percentage descending
    assert scale.rules[0].grade_letter == 'O'
    assert scale.rules[1].grade_letter == 'F'
