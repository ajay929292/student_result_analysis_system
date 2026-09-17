from functools import wraps
from flask import session, request, redirect, url_for, flash, jsonify


def login_required(f):
    """Ensure user is logged in before accessing route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Check if this is an API call
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'Authentication required', 'code': 'UNAUTHORIZED'}), 401
            
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """Decorator to enforce specific user roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({'error': 'Authentication required', 'code': 'UNAUTHORIZED'}), 401
                flash('Please log in to continue.', 'warning')
                return redirect(url_for('auth.login', next=request.path))

            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                if request.path.startswith('/api/') or request.is_json:
                    return jsonify({'error': 'Insufficient permissions', 'code': 'FORBIDDEN'}), 403
                flash('Access denied: You do not have permission to access this resource.', 'danger')
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Ensure user has Administrator role."""
    return role_required('ADMIN')(f)


def teacher_required(f):
    """Ensure user has Teacher or Administrator role."""
    return role_required('ADMIN', 'TEACHER')(f)
