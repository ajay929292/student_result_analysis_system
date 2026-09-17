"""Routes package."""

from app.routes.main_routes import main_bp
from app.routes.auth_routes import auth_bp
from app.routes.academic_routes import academic_bp
from app.routes.student_routes import student_bp
from app.routes.marks_routes import marks_bp
from app.routes.analytics_routes import analytics_bp

__all__ = ['main_bp', 'auth_bp', 'academic_bp', 'student_bp', 'marks_bp', 'analytics_bp']

