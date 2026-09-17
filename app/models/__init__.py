"""Models package exporting all SQLAlchemy entity models."""

from app.models.user import User
from app.models.academic import AcademicYear, Class, Subject, ClassSubject
from app.models.student import Student
from app.models.result import ExamTerm, GradingScale, GradeRule, Marks

__all__ = [
    'User',
    'AcademicYear',
    'Class',
    'Subject',
    'ClassSubject',
    'Student',
    'ExamTerm',
    'GradingScale',
    'GradeRule',
    'Marks'
]
