import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import event
from sqlalchemy.engine import Engine
from app.config import config

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()


# Enforce foreign key constraints on SQLite connections
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys=ON")
    except Exception:
        pass
    finally:
        cursor.close()


def create_app(config_name=None):
    """Application Factory pattern implementation."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    selected_config = config.get(config_name, config['default'])
    app.config.from_object(selected_config)

    # Ensure instance and upload directories exist
    os.makedirs(app.instance_path, exist_ok=True)
    if 'UPLOAD_FOLDER' in app.config:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Context processors for templates
    @app.context_processor
    def inject_global_vars():
        current_user = None
        if 'user_id' in session:
            current_user = {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'name': session.get('user_name'),
                'role': session.get('user_role'),
                'is_admin': session.get('user_role') == 'ADMIN',
                'is_teacher': session.get('user_role') in ['ADMIN', 'TEACHER']
            }
        return {
            'app_name': app.config.get('APP_NAME', 'Student Result Analysis System'),
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'current_env': config_name,
            'current_user': current_user
        }

    # Register Blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.academic_routes import academic_bp
    from app.routes.student_routes import student_bp
    from app.routes.marks_routes import marks_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.report_routes import reports_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(reports_bp)

    return app
