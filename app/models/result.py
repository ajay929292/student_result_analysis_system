from datetime import datetime, timezone
from app import db


class ExamTerm(db.Model):
    """Examination term / cycle (e.g., TEE June 2025, TEE December 2025)."""
    __tablename__ = 'exam_terms'

    term_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term_name = db.Column(db.String(50), nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id', ondelete='CASCADE'), nullable=False)
    is_locked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, term_name=None, year_id=None, is_locked=False, **kwargs):
        super().__init__(**kwargs)
        if term_name is not None:
            self.term_name = term_name
        if year_id is not None:
            self.year_id = year_id
        self.is_locked = is_locked

    # Relationships
    academic_year = db.relationship('AcademicYear', back_populates='terms')
    marks = db.relationship('Marks', back_populates='term', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'term_id': self.term_id,
            'term_name': self.term_name,
            'year_id': self.year_id,
            'year_label': self.academic_year.year_label if self.academic_year else None,
            'is_locked': self.is_locked
        }

    def __repr__(self):
        return f"<ExamTerm {self.term_name}>"


class GradingScale(db.Model):
    """Grading standard definition (e.g. IGNOU Standard 10-Point)."""
    __tablename__ = 'grading_scales'

    scale_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scale_name = db.Column(db.String(50), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, scale_name=None, is_active=True, **kwargs):
        super().__init__(**kwargs)
        if scale_name is not None:
            self.scale_name = scale_name
        self.is_active = is_active

    # Relationships
    rules = db.relationship(
        'GradeRule',
        back_populates='scale',
        cascade='all, delete-orphan',
        order_by='desc(GradeRule.min_percentage)'
    )

    def to_dict(self):
        return {
            'scale_id': self.scale_id,
            'scale_name': self.scale_name,
            'is_active': self.is_active,
            'rules': [r.to_dict() for r in self.rules]
        }

    def __repr__(self):
        return f"<GradingScale {self.scale_name}>"


class GradeRule(db.Model):
    """Specific grade bracket rule (e.g., A+ for 75% to 84.99%, Grade Point 9.0)."""
    __tablename__ = 'grade_rules'

    rule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scale_id = db.Column(db.Integer, db.ForeignKey('grading_scales.scale_id', ondelete='CASCADE'), nullable=False)
    min_percentage = db.Column(db.Float, nullable=False)
    max_percentage = db.Column(db.Float, nullable=False)
    grade_letter = db.Column(db.String(5), nullable=False)
    grade_point = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(50), nullable=False)

    def __init__(self, scale_id=None, min_percentage=None, max_percentage=None, grade_letter=None, grade_point=None, description=None, **kwargs):
        super().__init__(**kwargs)
        if scale_id is not None:
            self.scale_id = scale_id
        if min_percentage is not None:
            self.min_percentage = min_percentage
        if max_percentage is not None:
            self.max_percentage = max_percentage
        if grade_letter is not None:
            self.grade_letter = grade_letter
        if grade_point is not None:
            self.grade_point = grade_point
        if description is not None:
            self.description = description

    # Relationships
    scale = db.relationship('GradingScale', back_populates='rules')

    def to_dict(self):
        return {
            'rule_id': self.rule_id,
            'scale_id': self.scale_id,
            'min_percentage': self.min_percentage,
            'max_percentage': self.max_percentage,
            'grade_letter': self.grade_letter,
            'grade_point': self.grade_point,
            'description': self.description
        }

    def __repr__(self):
        return f"<GradeRule {self.grade_letter} ({self.min_percentage}-{self.max_percentage}%)>"


class Marks(db.Model):
    """Subject examination score record for a student in an exam term."""
    __tablename__ = 'marks'
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_subject_id', 'term_id', name='uq_student_subject_term'),
    )

    mark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    class_subject_id = db.Column(db.Integer, db.ForeignKey('class_subjects.class_subject_id', ondelete='CASCADE'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('exam_terms.term_id', ondelete='CASCADE'), nullable=False)
    
    internal_marks = db.Column(db.Float, default=0.0, nullable=False)
    external_marks = db.Column(db.Float, default=0.0, nullable=False)
    total_marks = db.Column(db.Float, default=0.0, nullable=False)
    percentage = db.Column(db.Float, default=0.0, nullable=False)
    grade = db.Column(db.String(5), nullable=True)
    grade_point = db.Column(db.Float, nullable=True)
    is_absent = db.Column(db.Boolean, default=False, nullable=False)
    is_passed = db.Column(db.Boolean, default=False, nullable=False)
    
    updated_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, student_id=None, class_subject_id=None, term_id=None, internal_marks=0.0, external_marks=0.0, total_marks=0.0, percentage=0.0, grade=None, grade_point=None, is_absent=False, is_passed=False, updated_by=None, **kwargs):
        super().__init__(**kwargs)
        if student_id is not None:
            self.student_id = student_id
        if class_subject_id is not None:
            self.class_subject_id = class_subject_id
        if term_id is not None:
            self.term_id = term_id
        self.internal_marks = internal_marks
        self.external_marks = external_marks
        self.total_marks = total_marks
        self.percentage = percentage
        if grade is not None:
            self.grade = grade
        if grade_point is not None:
            self.grade_point = grade_point
        self.is_absent = is_absent
        self.is_passed = is_passed
        if updated_by is not None:
            self.updated_by = updated_by

    # Relationships
    student = db.relationship('Student', back_populates='marks_records')
    class_subject = db.relationship('ClassSubject', back_populates='marks_records')
    term = db.relationship('ExamTerm', back_populates='marks')
    editor = db.relationship('User', foreign_keys=[updated_by])

    def calculate(self, class_subject=None, scale=None):
        """Compute total marks, percentage, pass status, and letter grade."""
        target_cs = class_subject or self.class_subject
        if not target_cs and self.class_subject_id:
            from app.models.academic import ClassSubject
            target_cs = db.session.get(ClassSubject, self.class_subject_id)

        max_in = target_cs.max_internal_marks if target_cs else 30.0
        max_ex = target_cs.max_external_marks if target_cs else 70.0
        pass_m = target_cs.pass_marks if target_cs else 40.0

        from app.services.grading_service import GradingService
        res = GradingService.evaluate(
            internal_marks=self.internal_marks,
            external_marks=self.external_marks,
            max_internal=max_in,
            max_external=max_ex,
            pass_marks=pass_m,
            is_absent=self.is_absent,
            scale=scale
        )
        self.internal_marks = res['internal_marks']
        self.external_marks = res['external_marks']
        self.total_marks = res['total_marks']
        self.percentage = res['percentage']
        self.is_absent = res['is_absent']
        self.is_passed = res['is_passed']
        self.grade = res['grade']
        self.grade_point = res['grade_point']

    def to_dict(self):
        return {
            'mark_id': self.mark_id,
            'student_id': self.student_id,
            'enrollment_no': self.student.enrollment_no if self.student else None,
            'student_name': self.student.full_name if self.student else None,
            'class_subject_id': self.class_subject_id,
            'subject_code': self.class_subject.subject_ref.subject_code if (self.class_subject and self.class_subject.subject_ref) else None,
            'term_id': self.term_id,
            'internal_marks': self.internal_marks,
            'external_marks': self.external_marks,
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'grade': self.grade,
            'grade_point': self.grade_point,
            'is_absent': self.is_absent,
            'is_passed': self.is_passed,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f"<Marks Student:{self.student_id} Sub:{self.class_subject_id} Total:{self.total_marks}>"
