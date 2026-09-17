from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from urllib.parse import urlparse, urljoin
from app.models import User
from app.utils.decorators import login_required

auth_bp = Blueprint('auth', __name__)


def is_safe_url(target):
    """Ensure redirect target is a safe internal relative path."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login and authentication."""
    # Redirect already authenticated users
    if 'user_id' in session:
        return redirect(url_for('main.index'))

    next_page = request.args.get('next', '')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Both username and password are required.', 'warning')
            return render_template('auth/login.html', next=next_page, username=username), 400

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact the administrator.', 'danger')
                return render_template('auth/login.html', next=next_page, username=username), 403

            # Regenerate session to prevent session fixation attacks
            session.clear()
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['user_role'] = user.role
            session['user_name'] = user.full_name

            flash(f'Welcome back, {user.full_name}!', 'success')

            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for('main.index'))

        flash('Invalid username or password. Please verify your credentials.', 'danger')
        return render_template('auth/login.html', next=next_page, username=username), 401

    return render_template('auth/login.html', next=next_page)


@auth_bp.route('/logout')
def logout():
    """Handle user session termination."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """View current user profile."""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User account not found.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/profile.html', user=user)


@auth_bp.route('/api/session')
def session_status():
    """JSON API to check current session state."""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('user_role'),
            'full_name': session.get('user_name')
        }), 200

    return jsonify({
        'authenticated': False,
        'user': None
    }), 200
