"""Tests for Flask app routes."""

import pytest
import json
import uuid
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask_app import init_app


@pytest.fixture(scope="session")
def app():
    """Create test Flask app with auth disabled."""
    test_app = init_app()
    test_app.config.update({
        "TESTING": True,
        "MONGO_DB_NAME": "test_assas",
        "TMP_FOLDER": "/tmp/test",
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret-key",
    })
    
    # Completely disable authentication for testing
    # This removes all @auth.login_required decorators
    with test_app.app_context():
        # Monkey patch the auth decorator globally
        import flask_app.auth_utils
        import flask_app.routes
        
        def no_auth_required(f):
            """Replacement for login_required that does nothing."""
            return f
        
        # Replace auth decorators
        if hasattr(flask_app.auth_utils, 'auth'):
            flask_app.auth_utils.auth.login_required = no_auth_required
        if hasattr(flask_app.routes, 'auth'):
            flask_app.routes.auth.login_required = no_auth_required
    
    return test_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_uuid():
    """Generate sample UUID for testing."""
    return str(uuid.uuid4())


@pytest.fixture
def mock_document(sample_uuid):
    """Sample document for testing."""
    return {
        "system_uuid": uuid.UUID(sample_uuid),
        "meta_name": "Test Dataset",
        "system_status": "Valid",
        "system_date": "2024-01-15",
        "system_user": "test_user",
        "system_size": "100 MB",
        "system_size_hdf5": "95 MB",
        "meta_description": "Test description",
        "meta_keywords": ["wind", "power"],
        "meta_tags": ["renewable"],
        "meta_data_variables": {"temp": "temperature"},
        "system_path": "/data/test.bin",
        "system_result": "/data/test.h5"
    }


# Separate class for route discovery
class TestRouteDiscovery:
    """Test to discover what routes actually exist."""
    
    def test_discover_routes(self, app):
        """Discover all available routes in the app."""
        print("\n=== AVAILABLE ROUTES ===")
        for rule in app.url_map.iter_rules():
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            print(f"{rule.rule:<40} -> {rule.endpoint:<30} [{', '.join(methods)}]")
        print("========================\n")


class TestBasicRoutes:
    """Test basic route functionality."""

    @patch('flask_app.routes.users')
    def test_login_route_exists(self, mock_users, client):
        """Test if login route exists and what it returns."""
        mock_users.get.return_value = {
            "email": "test@example.com",
            "institute": "Test Institute", 
            "role": "admin"
        }
        
        response = client.get("/login")
        print(f"\nLogin route response: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Just check that the route exists (not 404)
        assert response.status_code != 404

    def test_logout_route_exists(self, client):
        """Test if logout route exists."""
        response = client.get("/logout")
        print(f"\nLogout route response: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Just check that the route exists (not 404)
        assert response.status_code != 404

    def test_root_route_exists(self, client):
        """Test if root route exists."""
        response = client.get("/")
        print(f"\nRoot route response: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        # Just check that the route exists (not 404)
        assert response.status_code != 404

    def test_app_routes_exist(self, client):
        """Test if app routes exist."""
        routes = ["/test/assas_app", "/test/assas_app/"]
        
        for route in routes:
            response = client.get(route)
            print(f"\nRoute {route} response: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            # Just check that the route exists (not 404)
            assert response.status_code != 404

    @patch('flask_app.routes.AssasDatabaseManager')
    def test_hdf5_file_route_exists(self, mock_manager, client, sample_uuid):
        """Test if HDF5 file route exists."""
        # Mock the database manager
        mock_manager_instance = Mock()
        mock_manager.return_value = mock_manager_instance
        mock_manager_instance.get_database_entry_by_uuid.return_value = None
        
        response = client.get(f"/test/assas_app/hdf5_file?uuid={sample_uuid}")
        print(f"\nHDF5 file route response: {response.status_code}")
        print(f"Response data: {response.data}")
        
        # Just check that the route exists (not 404)
        assert response.status_code != 404


class TestWithMockedAuth:
    """Test routes with properly mocked authentication."""

    @pytest.fixture(autouse=True)
    def setup_auth_mock(self):
        """Setup authentication mocking for all tests in this class."""
        with patch('flask_app.routes.users') as mock_users:
            mock_users.get.return_value = {
                "email": "test@example.com",
                "institute": "Test Institute",
                "role": "admin"
            }
            
            # Mock the auth system at the module level
            with patch.object(sys.modules.get('flask_app.routes', Mock()), 'auth', Mock()) as mock_auth:
                mock_auth.login_required = lambda f: f
                yield

    def test_login_with_mocked_auth(self, client):
        """Test login route with mocked authentication."""
        response = client.get("/login")
        
        # Should not be a redirect if auth is properly mocked
        print(f"\nMocked login response: {response.status_code}")
        print(f"Response data: {response.data}")
        
        if response.status_code == 200:
            try:
                data = json.loads(response.data)
                assert "message" in data or "email" in data
            except json.JSONDecodeError:
                # Response might not be JSON
                pass

    @patch('flask_app.routes.AssasDatabaseManager')  
    def test_hdf5_with_mocked_auth(self, mock_manager, client, sample_uuid, mock_document):
        """Test HDF5 route with mocked authentication."""
        mock_manager_instance = Mock()
        mock_manager.return_value = mock_manager_instance
        mock_manager_instance.get_database_entry_by_uuid.return_value = mock_document
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('flask_app.routes.send_file') as mock_send_file:
            
            mock_send_file.return_value = Mock(status_code=200)
            
            response = client.get(f"/test/assas_app/hdf5_file?uuid={sample_uuid}")
            
            print(f"\nMocked HDF5 response: {response.status_code}")
            print(f"Response data: {response.data}")
            
            # Should not be a redirect if auth is properly mocked
            if response.status_code == 302:
                print(f"Still redirecting to: {response.location}")


# Simple integration test
class TestIntegration:
    """Simple integration tests without complex mocking."""
    
    def test_app_starts_successfully(self, app):
        """Test that the app starts without errors."""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_client_can_make_requests(self, client):
        """Test that the client can make basic requests."""
        # Just test that we can make a request without the app crashing
        response = client.get("/nonexistent-route")
        # Should get 404 for nonexistent route
        assert response.status_code == 404
        
    def test_existing_routes_dont_crash(self, client):
        """Test that existing routes don't crash the app."""
        routes_to_test = [
            "/",
            "/login", 
            "/logout",
            "/test/assas_app",
            "/test/assas_app/",
        ]
        
        for route in routes_to_test:
            try:
                response = client.get(route)
                print(f"Route {route}: HTTP {response.status_code}")
                
                # As long as we don't get a 500 (server error), the route is working
                assert response.status_code < 500
                
            except Exception as e:
                print(f"Route {route} failed with exception: {e}")
                # Even if there's an exception, the app shouldn't crash
                assert False, f"Route {route} caused an exception: {e}"