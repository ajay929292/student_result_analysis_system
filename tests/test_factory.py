import pytest
from app import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def test_config():
    """Test environment configuration switching."""
    dev_app = create_app('development')
    assert dev_app.config['DEBUG'] is True
    assert dev_app.config['TESTING'] is False

    test_app = create_app('testing')
    assert test_app.config['DEBUG'] is False
    assert test_app.config['TESTING'] is True
    assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'


def test_health_route(client):
    """Test the /health API endpoint returns 200 and healthy JSON."""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'ok'
    assert 'version' in json_data
    assert json_data['testing'] is True


def test_index_route(client):
    """Test the / root page loads successfully with HTML content."""
    response = client.get('/')
    assert response.status_code == 200
    html_content = response.get_data(as_text=True)
    assert 'Student Result Analysis System' in html_content
    assert 'Phase 0 / Phase 1 Active' in html_content
    assert 'SRAS Portal' in html_content


def test_not_found(client):
    """Test unhandled routes return 404."""
    response = client.get('/this-route-does-not-exist')
    assert response.status_code == 404
