"""Unit and Integration Tests for Phase 5 Analytics Engine & REST APIs."""

import pytest
from app import create_app, db
from app.models import (
    User, AcademicYear, Class, Subject, ClassSubject, Student,
    ExamTerm, Marks, GradingScale, GradeRule
)
from app.services.analytics_service import AnalyticsService


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

        # Seed Academic Hierarchy
        year = AcademicYear(year_label='2025-2026', is_active=True)
        db.session.add(year)
        db.session.flush()

        cls1 = Class(class_name='BCA-Sem-1', section='A', year_id=year.year_id)
        cls_empty = Class(class_name='BCA-Sem-2', section='A', year_id=year.year_id)
        sub1 = Subject(subject_code='BCS-011', subject_name='Computer Basics', credits=3)
        sub2 = Subject(subject_code='BCS-012', subject_name='Mathematics', credits=4)
        term1 = ExamTerm(term_name='TEE June 2025', year_id=year.year_id, is_locked=False)
        db.session.add_all([cls1, cls_empty, sub1, sub2, term1])
        db.session.flush()

        # Mappings
        map1 = ClassSubject(class_id=cls1.class_id, subject_id=sub1.subject_id, max_internal_marks=30.0, max_external_marks=70.0, pass_marks=40.0)
        map2 = ClassSubject(class_id=cls1.class_id, subject_id=sub2.subject_id, max_internal_marks=30.0, max_external_marks=70.0, pass_marks=40.0)
        db.session.add_all([map1, map2])
        db.session.flush()

        # Seed 4 Students
        st1 = Student(enrollment_no='230101', full_name='Alice Top', class_id=cls1.class_id)
        st2 = Student(enrollment_no='230102', full_name='Bob Pass', class_id=cls1.class_id)
        st3 = Student(enrollment_no='230103', full_name='Charlie Border', class_id=cls1.class_id)
        st4 = Student(enrollment_no='230104', full_name='David Fail', class_id=cls1.class_id)
        db.session.add_all([st1, st2, st3, st4])
        db.session.flush()

        # Seed Marks for Term 1
        # Alice Top: sub1 = 28+62=90 (O), sub2 = 27+61=88 (O) -> Passed both
        m1 = Marks(student_id=st1.student_id, class_subject_id=map1.class_subject_id, term_id=term1.term_id, internal_marks=28.0, external_marks=62.0)
        m1.calculate(class_subject=map1, scale=scale)
        m2 = Marks(student_id=st1.student_id, class_subject_id=map2.class_subject_id, term_id=term1.term_id, internal_marks=27.0, external_marks=61.0)
        m2.calculate(class_subject=map2, scale=scale)

        # Bob Pass: sub1 = 20+50=70 (A), sub2 = 18+47=65 (A) -> Passed both
        m3 = Marks(student_id=st2.student_id, class_subject_id=map1.class_subject_id, term_id=term1.term_id, internal_marks=20.0, external_marks=50.0)
        m3.calculate(class_subject=map1, scale=scale)
        m4 = Marks(student_id=st2.student_id, class_subject_id=map2.class_subject_id, term_id=term1.term_id, internal_marks=18.0, external_marks=47.0)
        m4.calculate(class_subject=map2, scale=scale)

        # Charlie Border: sub1 = 15+28=43 (C, Borderline), sub2 = 14+28=42 (C, Borderline) -> Passed both borderline
        m5 = Marks(student_id=st3.student_id, class_subject_id=map1.class_subject_id, term_id=term1.term_id, internal_marks=15.0, external_marks=28.0)
        m5.calculate(class_subject=map1, scale=scale)
        m6 = Marks(student_id=st3.student_id, class_subject_id=map2.class_subject_id, term_id=term1.term_id, internal_marks=14.0, external_marks=28.0)
        m6.calculate(class_subject=map2, scale=scale)

        # David Fail: sub1 = 10+20=30 (F), sub2 = 0+0=0 (Absent) -> Failed 1, absent 1
        m7 = Marks(student_id=st4.student_id, class_subject_id=map1.class_subject_id, term_id=term1.term_id, internal_marks=10.0, external_marks=20.0)
        m7.calculate(class_subject=map1, scale=scale)
        m8 = Marks(student_id=st4.student_id, class_subject_id=map2.class_subject_id, term_id=term1.term_id, internal_marks=0.0, external_marks=0.0, is_absent=True)
        m8.calculate(class_subject=map2, scale=scale)

        db.session.add_all([m1, m2, m3, m4, m5, m6, m7, m8])
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login_as(client, username, password):
    return client.post('/login', data={'username': username, 'password': password}, follow_redirects=True)


# ------------------------------------------------------------------------------
# Unit Tests for AnalyticsService
# ------------------------------------------------------------------------------

def test_analytics_empty_data(app):
    """Test AnalyticsService handles classes with zero records gracefully."""
    with app.app_context():
        empty_cls = Class.query.filter_by(class_name='BCA-Sem-2').first()
        term = ExamTerm.query.first()

        overview = AnalyticsService.compute_overview_metrics(empty_cls.class_id, term.term_id)
        assert overview['has_data'] is False
        assert overview['total_enrolled'] == 0
        assert overview['class_average'] == 0.0

        grades = AnalyticsService.compute_grade_distribution(empty_cls.class_id, term.term_id)
        assert grades['total_evaluations'] == 0
        assert all(c == 0 for c in grades['counts'])

        subjs = AnalyticsService.compute_subject_comparison(empty_cls.class_id, term.term_id)
        assert subjs['subjects'] == []

        at_risk = AnalyticsService.identify_at_risk_students(empty_cls.class_id, term.term_id)
        assert at_risk == []

        top_perf = AnalyticsService.compute_top_performers(empty_cls.class_id, term.term_id)
        assert top_perf == []


def test_analytics_overview_metrics(app):
    """Test vectorized overview metrics computation with active class records."""
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()

        overview = AnalyticsService.compute_overview_metrics(cls1.class_id, term1.term_id)
        assert overview['has_data'] is True
        assert overview['total_enrolled'] == 4
        assert overview['total_appeared'] == 4
        # Alice, Bob, Charlie passed all their exams (3 passed)
        # David failed BCS-011 (1 failed)
        assert overview['total_passed'] == 3
        assert overview['total_failed'] == 1
        assert overview['pass_percentage'] == 75.0

        # Alice average is 89%, Bob is 67.5%, Charlie is 42.5%, David is 30%
        # Mean = (89 + 67.5 + 42.5 + 30) / 4 = 57.25%
        assert overview['class_average'] == 57.25
        assert overview['highest_score'] == 89.0
        assert overview['lowest_score'] == 30.0

        assert overview['top_student'] is not None
        assert overview['top_student']['student_name'] == 'Alice Top'
        assert overview['top_student']['grade'] == 'O'


def test_analytics_grade_distribution(app):
    """Test frequency distribution across IGNOU 10-point grades."""
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()

        dist = AnalyticsService.compute_grade_distribution(cls1.class_id, term1.term_id)
        # Total evaluations = 8
        assert dist['total_evaluations'] == 8

        labels = dist['labels']
        counts = dist['counts']
        grade_map = dict(zip(labels, counts))

        # Alice: 2 'O's
        assert grade_map['O'] == 2
        # Bob: 2 'A's
        assert grade_map['A'] == 2
        # Charlie: 2 'C's
        assert grade_map['C'] == 2
        # David: 2 'F's (1 failed score 30%, 1 absent)
        assert grade_map['F'] == 2


def test_analytics_subject_comparison(app):
    """Test cross-subject comparison metrics and challenging course identification."""
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()

        data = AnalyticsService.compute_subject_comparison(cls1.class_id, term1.term_id)
        subjects = data['subjects']
        assert len(subjects) == 2

        sub_codes = [s['subject_code'] for s in subjects]
        assert 'BCS-011' in sub_codes
        assert 'BCS-012' in sub_codes

        # In BCS-011: 4 appeared, 3 passed, 1 failed -> 75% pass rate
        bcs011 = next(s for s in subjects if s['subject_code'] == 'BCS-011')
        assert bcs011['appeared'] == 4
        assert bcs011['passed'] == 3
        assert bcs011['pass_rate'] == 75.0

        # In BCS-012: 3 appeared, 1 absent. All 3 passed -> 100% pass rate
        bcs012 = next(s for s in subjects if s['subject_code'] == 'BCS-012')
        assert bcs012['appeared'] == 3
        assert bcs012['absent'] == 1
        assert bcs012['passed'] == 3
        assert bcs012['pass_rate'] == 100.0

        # Most challenging subject should be BCS-011 due to lower pass rate
        assert data['most_challenging']['subject_code'] == 'BCS-011'


def test_analytics_at_risk_students(app):
    """Test detection of at-risk students: failing subjects, borderline scores, and absenteeism."""
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()

        at_risk = AnalyticsService.identify_at_risk_students(cls1.class_id, term1.term_id)
        assert len(at_risk) >= 2

        names = [r['student_name'] for r in at_risk]
        assert 'David Fail' in names
        assert 'Charlie Border' in names
        # Alice and Bob should NOT be at risk
        assert 'Alice Top' not in names
        assert 'Bob Pass' not in names

        david = next(r for r in at_risk if r['student_name'] == 'David Fail')
        assert david['failed_count'] == 1
        assert 'BCS-011' in david['failed_subjects']

        charlie = next(r for r in at_risk if r['student_name'] == 'Charlie Border')
        assert any('Borderline' in reason for reason in charlie['reasons'])


def test_analytics_top_performers(app):
    """Test ranking of top performers ordered by percentage."""
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()

        top_list = AnalyticsService.compute_top_performers(cls1.class_id, term1.term_id, limit=3)
        assert len(top_list) <= 3
        assert top_list[0]['student_name'] == 'Alice Top'
        assert top_list[0]['rank'] == 1
        assert top_list[0]['grade'] == 'O'
        assert top_list[1]['student_name'] == 'Bob Pass'
        assert top_list[1]['rank'] == 2


# ------------------------------------------------------------------------------
# Integration Tests for REST API Endpoints
# ------------------------------------------------------------------------------

def test_api_analytics_unauthorized(client):
    """Test unauthenticated API access returns 401."""
    resp = client.get('/api/analytics/overview?class_id=1&term_id=1')
    assert resp.status_code == 401
    data = resp.get_json()
    assert data['code'] == 'UNAUTHORIZED'


def test_api_analytics_missing_params(client):
    """Test missing query parameters returns 400 Bad Request."""
    login_as(client, 'teacher', 'Teacher@123')
    resp = client.get('/api/analytics/overview')
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['code'] == 'BAD_REQUEST'


def test_api_analytics_overview(app, client):
    """Test GET /api/analytics/overview returns 200 and valid JSON schema."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/api/analytics/overview?class_id={c_id}&term_id={t_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['has_data'] is True
    assert 'class_average' in data
    assert 'pass_percentage' in data
    assert 'top_student' in data


def test_api_analytics_grade_distribution(app, client):
    """Test GET /api/analytics/grade-distribution returns 200 and grade data."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/api/analytics/grade-distribution?class_id={c_id}&term_id={t_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'labels' in data
    assert 'counts' in data
    assert len(data['labels']) == 7


def test_api_analytics_subject_comparison(app, client):
    """Test GET /api/analytics/subject-comparison returns 200 and subject data."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/api/analytics/subject-comparison?class_id={c_id}&term_id={t_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'subjects' in data
    assert len(data['subjects']) == 2
    assert 'most_challenging' in data


def test_api_analytics_at_risk(app, client):
    """Test GET /api/analytics/at-risk returns 200 and candidate alerts."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/api/analytics/at-risk?class_id={c_id}&term_id={t_id}')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'at_risk_students' in data
    assert data['count'] >= 2


def test_api_analytics_top_performers(app, client):
    """Test GET /api/analytics/top-performers returns 200 and rankers."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/api/analytics/top-performers?class_id={c_id}&term_id={t_id}&limit=2')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'top_performers' in data
    assert len(data['top_performers']) <= 2


def test_web_analytics_dashboard(app, client):
    """Test authenticated teacher loading /analytics web page."""
    login_as(client, 'teacher', 'Teacher@123')
    with app.app_context():
        cls1 = Class.query.filter_by(class_name='BCA-Sem-1').first()
        term1 = ExamTerm.query.first()
        c_id, t_id = cls1.class_id, term1.term_id

    resp = client.get(f'/analytics?class_id={c_id}&term_id={t_id}')
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert 'Statistical Analytics & Academic Intelligence' in html
    assert 'Cohort Mean Score' in html
    assert 'Overall Pass Rate' in html
    assert 'Academic Merit Board' in html
    assert 'gradeDistributionChart' in html
    assert 'subjectComparisonChart' in html
    assert 'outcomeDoughnutChart' in html
