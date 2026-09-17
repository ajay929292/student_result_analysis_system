import pytest
from flask import session
from app import create_app, db
from app.models import User
from app.utils.decorators import login_required, admin_required, teacher_required


@pytest.fixture
def app():
    """Create test application configured with an in-memory database."""
    app = create_app('testing')

    # Register temporary test routes to verify RBAC decorators
    @app.route('/test-protected')
    @login_required
    def protected_route():
        return 'Protected Content', 200

    @app.route('/test-admin-only')
    @admin_required
    def admin_only_route():
        return 'Admin Content', 200

    @app.route('/test-teacher-only')
    @teacher_required
    def teacher_only_route():
        return 'Teacher Content', 200

    with app.app_context():
        db.create_all()

        # Create seeded test users
        admin = User(username='admin', full_name='Admin User', role=User.ROLE_ADMIN)
        admin.set_password('Admin@123')

        teacher = User(username='teacher', full_name='Teacher User', role=User.ROLE_TEACHER)
        teacher.set_password('Teacher@123')

        student = User(username='student', full_name='Student User', role=User.ROLE_STUDENT)
        student.set_password('Student@123')

        inactive = User(username='disabled', full_name='Inactive User', role=User.ROLE_STUDENT, is_active=False)
        inactive.set_password('Inactive@123')

        db.session.add_all([admin, teacher, student, inactive])
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_login_page_renders(client):
    """Verify login page renders properly with 200 status."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Portal Authentication' in response.data
    assert b'Username or Enrollment No' in response.data


def test_login_success(client):
    """Verify successful login sets session and redirects."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'Admin@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert sess['user_id'] is not None
        assert sess['username'] == 'admin'
        assert sess['user_role'] == 'ADMIN'


def test_login_invalid_password(client):
    """Verify invalid credentials return 401 and error message."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'WrongPassword'
    })
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data


def test_login_inactive_user(client):
    """Verify inactive account is blocked with 403."""
    response = client.post('/login', data={
        'username': 'disabled',
        'password': 'Inactive@123'
    })
    assert response.status_code == 403
    assert b'account has been deactivated' in response.data


def test_logout(client):
    """Verify logout clears session and redirects to login."""
    # First log in
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'})
    with client.session_transaction() as sess:
        assert 'user_id' in sess

    # Then log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out successfully' in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess


def test_rbac_login_required(client):
    """Verify unauthenticated requests are redirected to /login."""
    response = client.get('/test-protected')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_rbac_admin_required(client):
    """Verify @admin_required permits ADMIN and blocks TEACHER / STUDENT."""
    # Teacher tries to access admin-only route
    client.post('/login', data={'username': 'teacher', 'password': 'Teacher@123'})
    response = client.get('/test-admin-only', follow_redirects=True)
    assert b'Access denied' in response.data

    # Logout and log in as Admin
    client.get('/logout')
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'})
    response = client.get('/test-admin-only')
    assert response.status_code == 200
    assert b'Admin Content' in response.data


def test_rbac_teacher_required(client):
    """Verify @teacher_required permits ADMIN and TEACHER, blocks STUDENT."""
    # Student tries to access teacher route
    client.post('/login', data={'username': 'student', 'password': 'Student@123'})
    response = client.get('/test-teacher-only', follow_redirects=True)
    assert b'Access denied' in response.data

    # Teacher accesses teacher route
    client.get('/logout')
    client.post('/login', data={'username': 'teacher', 'password': 'Teacher@123'})
    response = client.get('/test-teacher-only')
    assert response.status_code == 200
    assert b'Teacher Content' in response.data


def test_api_session_status(client):
    """Verify /api/session returns correct JSON authentication status."""
    # Unauthenticated
    res = client.get('/api/session')
    assert res.status_code == 200
    assert res.get_json()['authenticated'] is False

    # Authenticated
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'})
    res = client.get('/api/session')
    assert res.status_code == 200
    data = res.get_json()
    assert data['authenticated'] is True
    assert data['username'] == 'admin'
    assert data['role'] == 'ADMIN'
