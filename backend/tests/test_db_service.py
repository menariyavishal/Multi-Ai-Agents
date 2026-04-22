"""Tests for database service - Phase 3."""

import pytest
import sqlite3
import json
import tempfile
from pathlib import Path
from app.services.db_service import DatabaseService
import hashlib


@pytest.fixture
def temp_db():
    """Create temporary SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        # Create schema
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE api_keys (
                key_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE query_history (
                query_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT,
                query_text TEXT NOT NULL,
                query_hash TEXT,
                agent_outputs TEXT,
                status TEXT,
                error_message TEXT,
                execution_time_seconds REAL,
                iterations_used INTEGER,
                quality_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
        
        yield db_path


@pytest.fixture
def db_service(temp_db, monkeypatch):
    """Create DatabaseService with temporary database."""
    monkeypatch.setattr("app.services.db_service.DB_PATH", temp_db)
    service = DatabaseService()
    service.db_path = temp_db
    yield service
    service.close()
    
    # Force cleanup of any remaining connections
    import gc
    gc.collect()


class TestUserManagement:
    """Test user registration and management."""
    
    def test_register_user(self, db_service):
        """Test user registration."""
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        
        api_key = db_service.register_user(username, email, password_hash)
        
        assert api_key is not None
        assert api_key.startswith("sk_")
        assert len(api_key) > 20
    
    def test_register_duplicate_username(self, db_service):
        """Test registering duplicate username."""
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        
        # First registration should succeed
        api_key1 = db_service.register_user(username, email, password_hash)
        assert api_key1 is not None
        
        # Second registration with same username should fail
        api_key2 = db_service.register_user(username, "another@example.com", password_hash)
        assert api_key2 is None
    
    def test_register_duplicate_email(self, db_service):
        """Test registering duplicate email."""
        username1 = "testuser1"
        username2 = "testuser2"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        
        # First registration should succeed
        api_key1 = db_service.register_user(username1, email, password_hash)
        assert api_key1 is not None
        
        # Second registration with same email should fail
        api_key2 = db_service.register_user(username2, email, password_hash)
        assert api_key2 is None


class TestAPIKeyValidation:
    """Test API key validation."""
    
    def test_validate_api_key(self, db_service):
        """Test valid API key validation."""
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        
        api_key = db_service.register_user(username, email, password_hash)
        
        # Validate the API key
        user_id = db_service.validate_api_key(api_key)
        
        assert user_id is not None
        assert isinstance(user_id, str)
    
    def test_validate_invalid_api_key(self, db_service):
        """Test invalid API key."""
        user_id = db_service.validate_api_key("invalid_key_12345")
        
        assert user_id is None
    
    def test_validate_empty_api_key(self, db_service):
        """Test empty API key."""
        user_id = db_service.validate_api_key("")
        
        assert user_id is None


class TestQueryHistory:
    """Test query history operations."""
    
    def test_save_query_history(self, db_service):
        """Test saving query to history."""
        # First create a user
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        api_key = db_service.register_user(username, email, password_hash)
        user_id = db_service.validate_api_key(api_key)
        
        # Save query
        query_text = "What is AI?"
        query_id = db_service.save_query_history(
            user_id=user_id,
            query_text=query_text,
            session_id="session_123",
            agent_outputs={"plan": "test plan"},
            status="completed",
            execution_time_seconds=5.5,
            iterations_used=1,
            quality_score=0.9
        )
        
        assert query_id is not None
        assert isinstance(query_id, str)
    
    def test_get_query_history(self, db_service):
        """Test retrieving query history."""
        # Create user and save queries
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        api_key = db_service.register_user(username, email, password_hash)
        user_id = db_service.validate_api_key(api_key)
        
        # Save multiple queries
        for i in range(3):
            db_service.save_query_history(
                user_id=user_id,
                query_text=f"Query {i}",
                status="completed",
                execution_time_seconds=float(i + 1),
                quality_score=0.9
            )
        
        # Retrieve history
        history = db_service.get_history(user_id, limit=10)
        
        assert len(history) == 3
        assert all("query_id" in record for record in history)
    
    def test_get_history_pagination(self, db_service):
        """Test history pagination."""
        # Create user and save many queries
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        api_key = db_service.register_user(username, email, password_hash)
        user_id = db_service.validate_api_key(api_key)
        
        # Save 15 queries
        for i in range(15):
            db_service.save_query_history(
                user_id=user_id,
                query_text=f"Query {i}",
                status="completed"
            )
        
        # Get first page (10 records)
        page1 = db_service.get_history(user_id, limit=10, offset=0)
        assert len(page1) == 10
        
        # Get second page (5 records)
        page2 = db_service.get_history(user_id, limit=10, offset=10)
        assert len(page2) == 5
    
    def test_save_query_with_agent_outputs(self, db_service):
        """Test saving query with structured agent outputs."""
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        api_key = db_service.register_user(username, email, password_hash)
        user_id = db_service.validate_api_key(api_key)
        
        agent_outputs = {
            "plan": "Research and analyze",
            "research": "Found data...",
            "analysis": {"patterns": ["A", "B"]},
            "draft": "The answer is...",
            "review": {"score": 0.95}
        }
        
        query_id = db_service.save_query_history(
            user_id=user_id,
            query_text="Complex query",
            agent_outputs=agent_outputs,
            status="completed"
        )
        
        # Retrieve and verify
        history = db_service.get_history(user_id)
        assert len(history) == 1
        assert history[0]["agent_outputs"] == agent_outputs
    
    def test_save_query_with_error(self, db_service):
        """Test saving query with error information."""
        username = "testuser"
        email = "test@example.com"
        password_hash = hashlib.sha256("password".encode()).hexdigest()
        api_key = db_service.register_user(username, email, password_hash)
        user_id = db_service.validate_api_key(api_key)
        
        query_id = db_service.save_query_history(
            user_id=user_id,
            query_text="Failed query",
            status="failed",
            error_message="API timeout",
            execution_time_seconds=30.0
        )
        
        history = db_service.get_history(user_id)
        assert len(history) == 1
        assert history[0]["status"] == "failed"
        assert history[0]["error_message"] == "API timeout"


class TestMongoDBOperations:
    """Test MongoDB operations (with mocking)."""
    
    def test_save_full_state_to_mongo_no_connection(self, db_service):
        """Test saving state when MongoDB is unavailable."""
        session_id = "session_123"
        query = "Test query"
        workflow_state = {"plan": "test", "status": "completed"}
        
        # Should handle gracefully without MongoDB
        result = db_service.save_full_state_to_mongo(
            session_id=session_id,
            query=query,
            workflow_state=workflow_state,
            status="completed"
        )
        
        # Should return False if MongoDB not available
        assert isinstance(result, bool)
    
    def test_get_full_state_from_mongo_no_connection(self, db_service):
        """Test retrieving state when MongoDB is unavailable."""
        state = db_service.get_full_state_from_mongo("session_123")
        
        # Should return None if MongoDB not available
        assert state is None


class TestDatabaseServiceSingleton:
    """Test singleton pattern."""
    
    def test_get_db_service(self):
        """Test getting database service singleton."""
        from app.services.db_service import get_db_service
        
        service1 = get_db_service()
        service2 = get_db_service()
        
        # Should be same instance
        assert service1 is service2
