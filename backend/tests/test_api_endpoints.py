"""Tests for Flask API endpoints - Phase 7."""

import pytest
import json
from app import create_app


@pytest.fixture
def app():
    """Create app for testing."""
    app = create_app(config_name="testing")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthCheck:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test /health endpoint."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'name' in data
        assert 'endpoints' in data


class TestQueryEndpoint:
    """Test /api/v1/query endpoint."""
    
    def test_query_missing_json(self, client):
        """Test query without JSON content-type."""
        response = client.post(
            '/api/v1/query',
            data="invalid"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_query_missing_query_field(self, client):
        """Test query without 'query' field."""
        response = client.post(
            '/api/v1/query',
            json={}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'required' in data['error'].lower()
    
    def test_query_empty_query(self, client):
        """Test query with empty string."""
        response = client.post(
            '/api/v1/query',
            json={"query": "   "}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_query_too_long(self, client):
        """Test query exceeding length limit."""
        long_query = "a" * 1001
        
        response = client.post(
            '/api/v1/query',
            json={"query": long_query}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
    
    @pytest.mark.slow
    def test_query_valid(self, client, groq_api_key):
        """Test valid query processing."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
        
        response = client.post(
            '/api/v1/query',
            json={"query": "What is 2+2?", "max_iterations": 1}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'session_id' in data
        assert 'result' in data
        assert 'final_answer' in data['result']
    
    def test_query_max_iterations_invalid(self, client):
        """Test max_iterations validation."""
        response = client.post(
            '/api/v1/query',
            json={"query": "test", "max_iterations": 10}
        )
        
        # Should either accept (normalized) or reject
        assert response.status_code in [200, 400]
    
    @pytest.mark.slow
    def test_query_response_structure(self, client, groq_api_key):
        """Test response structure for valid queries."""
        if not groq_api_key:
            pytest.skip("GROQ_API_KEY not set")
            
        response = client.post(
            '/api/v1/query',
            json={"query": "short"}
        )
        
        # Even if processing fails, structure should be consistent
        data = response.get_json()
        assert 'status' in data
        assert 'session_id' in data
        assert 'result' in data or 'error' in data


class TestHistoryEndpoint:
    """Test /api/v1/history endpoint."""
    
    def test_history_valid_query(self, client):
        """Test getting history for a query."""
        response = client.get('/api/v1/history/test_query')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'checkpoints' in data
    
    def test_history_empty_query_hash(self, client):
        """Test history with empty query hash."""
        response = client.get('/api/v1/history/')
        
        # 404 because URL is malformed
        assert response.status_code in [400, 404]


class TestCheckpointEndpoint:
    """Test /api/v1/checkpoint endpoint."""
    
    def test_checkpoint_valid(self, client):
        """Test retrieving a checkpoint."""
        response = client.get('/api/v1/checkpoint/test_checkpoint')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'


class TestRegisterEndpoint:
    """Test /api/v1/register endpoint."""
    
    def test_register_missing_json(self, client):
        """Test register without JSON."""
        response = client.post(
            '/api/v1/register',
            data="invalid"
        )
        
        assert response.status_code == 400
    
    def test_register_missing_username(self, client):
        """Test register without username."""
        response = client.post(
            '/api/v1/register',
            json={"email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'username' in data['error'].lower() or 'at least 3' in data['error'].lower()
    
    def test_register_short_username(self, client):
        """Test register with too short username."""
        response = client.post(
            '/api/v1/register',
            json={"username": "ab", "email": "test@example.com", "password": "password123"}
        )
        
        assert response.status_code == 400
    
    def test_register_invalid_email(self, client):
        """Test register with invalid email."""
        response = client.post(
            '/api/v1/register',
            json={"username": "testuser", "email": "invalid", "password": "password123"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data['error'].lower()
    
    def test_register_short_password(self, client):
        """Test register with too short password."""
        response = client.post(
            '/api/v1/register',
            json={"username": "testuser", "email": "test@example.com", "password": "short"}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'password' in data['error'].lower()
    
    def test_register_valid(self, client):
        """Test valid registration."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        response = client.post(
            '/api/v1/register',
            json={
                "username": f"testuser_{unique_id}",
                "email": f"test_{unique_id}@example.com",
                "password": "securepassword123"
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'api_key' in data
        assert 'user_id' in data
        assert data['api_key'].startswith('sk_')


class TestValidateKeyEndpoint:
    """Test /api/v1/validate-key endpoint."""
    
    def test_validate_key_missing_json(self, client):
        """Test validate without JSON."""
        response = client.post(
            '/api/v1/validate-key',
            data="invalid"
        )
        
        assert response.status_code == 400
    
    def test_validate_key_missing_key(self, client):
        """Test validate without api_key field."""
        response = client.post(
            '/api/v1/validate-key',
            json={}
        )
        
        assert response.status_code == 400
    
    def test_validate_key_invalid_format(self, client):
        """Test validate with invalid key format."""
        response = client.post(
            '/api/v1/validate-key',
            json={"api_key": "invalid_key"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['valid'] is False
    
    def test_validate_key_valid_format(self, client):
        """Test validate with valid key format."""
        response = client.post(
            '/api/v1/validate-key',
            json={"api_key": f"sk_{'a' * 32}"}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'valid' in data


class TestErrorHandlers:
    """Test error handling."""
    
    def test_404_not_found(self, client):
        """Test 404 error handler."""
        response = client.get('/nonexistent/endpoint')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['status'] == 'error'
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error handler."""
        response = client.delete('/api/v1/query')
        
        assert response.status_code == 405
        data = response.get_json()
        assert data['status'] == 'error'


@pytest.fixture(scope="session")
def groq_api_key():
    """Get Groq API key from environment."""
    import os
    return os.getenv("GROQ_API_KEY")
