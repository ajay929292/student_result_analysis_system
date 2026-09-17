from datetime import datetime, timezone
from app import db, bcrypt


class User(db.Model):
    """User account model for authentication and Role-Based Access Control (RBAC)."""
    __tablename__ = 'users'

    ROLE_ADMIN = 'ADMIN'
    ROLE_TEACHER = 'TEACHER'
    ROLE_STUDENT = 'STUDENT'
    VALID_ROLES = [ROLE_ADMIN, ROLE_TEACHER, ROLE_STUDENT]

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_STUDENT, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, username=None, role=ROLE_STUDENT, full_name=None, email=None, is_active=True, **kwargs):
        super().__init__(**kwargs)
        if username is not None:
            self.username = username
        if role is not None:
            self.role = role
        if full_name is not None:
            self.full_name = full_name
        if email is not None:
            self.email = email
        self.is_active = is_active

    def set_password(self, password):
        """Hash and set user password using bcrypt."""
        if not password or len(password.strip()) == 0:
            raise ValueError("Password cannot be empty.")
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password against stored bcrypt hash."""
        if not self.password_hash or not password:
            return False
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_teacher(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_TEACHER]

    def to_dict(self):
        """Return serialized user data (omits password hash)."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
