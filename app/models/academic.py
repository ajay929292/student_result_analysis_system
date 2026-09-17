from datetime import datetime, timezone
from app import db


class AcademicYear(db.Model):
    """Academic Year / Session entity (e.g., 2025-2026)."""
    __tablename__ = 'academic_years'

    year_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year_label = db.Column(db.String(20), unique=True, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, year_label=None, is_active=False, **kwargs):
        super().__init__(**kwargs)
        if year_label is not None:
            self.year_label = year_label
        self.is_active = is_active

    # Relationships
    classes = db.relationship('Class', back_populates='academic_year', cascade='all, delete-orphan')
    terms = db.relationship('ExamTerm', back_populates='academic_year', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'year_id': self.year_id,
            'year_label': self.year_label,
            'is_active': self.is_active,
            'class_count': len(self.classes) if self.classes else 0
        }

    def __repr__(self):
        return f"<AcademicYear {self.year_label} (active={self.is_active})>"


class Class(db.Model):
    """Degree program semester / batch cohort (e.g., BCA-Semester-1, Section A)."""
    __tablename__ = 'classes'
    __table_args__ = (
        db.UniqueConstraint('class_name', 'section', 'year_id', name='uq_class_section_year'),
    )

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10), default='A', nullable=False)
    year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, class_name=None, section='A', year_id=None, **kwargs):
        super().__init__(**kwargs)
        if class_name is not None:
            self.class_name = class_name
        self.section = section
        if year_id is not None:
            self.year_id = year_id

    # Relationships
    academic_year = db.relationship('AcademicYear', back_populates='classes')
    students = db.relationship('Student', back_populates='enrolled_class', cascade='all, delete-orphan')
    class_subjects = db.relationship('ClassSubject', back_populates='class_ref', cascade='all, delete-orphan')

    @property
    def display_name(self):
        return f"{self.class_name} - Sec {self.section}"

    def to_dict(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'section': self.section,
            'year_id': self.year_id,
            'display_name': self.display_name,
            'student_count': len(self.students) if self.students else 0
        }

    def __repr__(self):
        return f"<Class {self.display_name}>"


class Subject(db.Model):
    """Master registry for course subjects (e.g., BCS-011 Computer Basics)."""
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    subject_name = db.Column(db.String(100), nullable=False)
    credits = db.Column(db.Integer, default=4, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, subject_code=None, subject_name=None, credits=4, **kwargs):
        super().__init__(**kwargs)
        if subject_code is not None:
            self.subject_code = subject_code
        if subject_name is not None:
            self.subject_name = subject_name
        self.credits = credits

    # Relationships
    class_subjects = db.relationship('ClassSubject', back_populates='subject_ref', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'subject_id': self.subject_id,
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'credits': self.credits
        }

    def __repr__(self):
        return f"<Subject {self.subject_code} - {self.subject_name}>"


class ClassSubject(db.Model):
    """Curriculum mapping between Class and Subject with evaluation mark thresholds."""
    __tablename__ = 'class_subjects'
    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', name='uq_class_subject'),
    )

    class_subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    max_internal_marks = db.Column(db.Float, default=30.0, nullable=False)
    max_external_marks = db.Column(db.Float, default=70.0, nullable=False)
    pass_marks = db.Column(db.Float, default=40.0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, class_id=None, subject_id=None, max_internal_marks=30.0, max_external_marks=70.0, pass_marks=40.0, **kwargs):
        super().__init__(**kwargs)
        if class_id is not None:
            self.class_id = class_id
        if subject_id is not None:
            self.subject_id = subject_id
        self.max_internal_marks = max_internal_marks
        self.max_external_marks = max_external_marks
        self.pass_marks = pass_marks

    # Relationships
    class_ref = db.relationship('Class', back_populates='class_subjects')
    subject_ref = db.relationship('Subject', back_populates='class_subjects')
    marks_records = db.relationship('Marks', back_populates='class_subject', cascade='all, delete-orphan')

    @property
    def mapping_id(self):
        return self.class_subject_id

    @property
    def subject(self):
        return self.subject_ref

    @property
    def assigned_class(self):
        return self.class_ref

    @property
    def max_total_marks(self):
        return self.max_internal_marks + self.max_external_marks

    def to_dict(self):
        return {
            'class_subject_id': self.class_subject_id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'subject_code': self.subject_ref.subject_code if self.subject_ref else None,
            'subject_name': self.subject_ref.subject_name if self.subject_ref else None,
            'max_internal': self.max_internal_marks,
            'max_external': self.max_external_marks,
            'max_total': self.max_total_marks,
            'pass_marks': self.pass_marks
        }

    def __repr__(self):
        sub_code = self.subject_ref.subject_code if self.subject_ref else self.subject_id
        return f"<ClassSubject Class:{self.class_id} Sub:{sub_code}>"
