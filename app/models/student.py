from datetime import datetime, timezone
from app import db


class Student(db.Model):
    """Enrolled student profile."""
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enrollment_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, enrollment_no=None, full_name=None, email=None, class_id=None, **kwargs):
        super().__init__(**kwargs)
        if enrollment_no is not None:
            self.enrollment_no = enrollment_no
        if full_name is not None:
            self.full_name = full_name
        if email is not None:
            self.email = email
        if class_id is not None:
            self.class_id = class_id

    # Relationships
    enrolled_class = db.relationship('Class', back_populates='students')
    marks_records = db.relationship('Marks', back_populates='student', cascade='all, delete-orphan')

    @property
    def assigned_class(self):
        return self.enrolled_class

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'enrollment_no': self.enrollment_no,
            'full_name': self.full_name,
            'email': self.email,
            'class_id': self.class_id,
            'class_name': self.enrolled_class.display_name if self.enrolled_class else None
        }

    def __repr__(self):
        return f"<Student {self.enrollment_no} - {self.full_name}>"
