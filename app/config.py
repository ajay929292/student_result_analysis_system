import os
from pathlib import Path

# Base directory of the app package
basedir = Path(__file__).resolve().parent
# Project root directory
project_root = basedir.parent


class BaseConfig:
    """Base configuration with default settings."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-student-result-analysis-ignou-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = str(project_root / 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    APP_NAME = "Student Result Analysis System"
    APP_VERSION = "1.0.0"


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        f"sqlite:///{project_root / 'instance' / 'dev.db'}"
    )


class TestingConfig(BaseConfig):
    """Testing environment configuration with in-memory database."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{project_root / 'instance' / 'student_results.db'}"
    )


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
