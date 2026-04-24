"""Tests for MongoDB database service and conversation history."""

import pytest
import os
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.models.conversation import Conversation, UserProfile
from app.services.database_service import DatabaseService, get_db_service


class TestConversationModel:
    """Test Conversation Pydantic model."""
    
    def test_conversation_creation(self):
        """Test creating a conversation object."""
        conv = Conversation(
            user_id="user123",
            query="What is AI?",
            plan="Research current AI trends",
            research="Found multiple sources on AI",
            content="AI is artificial intelligence...",
            analysis={"key_insights": "AI is growing"},
            final_output="Comprehensive answer about AI",
            data_classification="COMBINED",
            quality_score=0.92,
            quality_level="high"
        )
        
        assert conv.user_id == "user123"
        assert conv.query == "What is AI?"
        assert conv.quality_score == 0.92
        assert conv.data_classification == "COMBINED"
        assert conv.conversation_id is not None
        assert conv.created_at is not None
    
    def test_conversation_dict_conversion(self):
        """Test converting conversation to dict."""
        conv = Conversation(
            user_id="user123",
            query="What is AI?",
            plan="Plan",
            research="Research",
            content="Content",
            analysis={},
            final_output="Output",
            data_classification="COMBINED",
            quality_score=0.9,
            quality_level="high"
        )
        
        conv_dict = conv.dict()
        assert isinstance(conv_dict, dict)
        assert conv_dict["user_id"] == "user123"
        assert conv_dict["quality_score"] == 0.9
    
    def test_conversation_default_values(self):
        """Test conversation default values."""
        conv = Conversation(
            user_id="user123",
            query="Test",
            plan="Plan",
            research="Research",
            content="Content",
            analysis={},
            final_output="Output",
            data_classification="REAL_TIME",
            quality_score=0.8,
            quality_level="medium"
        )
        
        assert conv.tags == []
        assert conv.processing_time_seconds is None
        assert isinstance(conv.created_at, datetime)


class TestUserProfileModel:
    """Test UserProfile Pydantic model."""
    
    def test_user_profile_creation(self):
        """Test creating a user profile."""
        user = UserProfile(
            user_id="user123",
            email="user@example.com",
            name="John Doe"
        )
        
        assert user.user_id == "user123"
        assert user.email == "user@example.com"
        assert user.name == "John Doe"
        assert user.total_conversations == 0
        assert user.average_quality_score == 0.0
    
    def test_user_profile_default_preferences(self):
        """Test user profile default preferences."""
        user = UserProfile(user_id="user123")
        
        assert user.preferred_data_classification == "COMBINED"
        assert user.theme == "light"
        assert user.total_conversations == 0


class TestDatabaseService:
    """Test DatabaseService class."""
    
    @pytest.fixture
    def mock_db_service(self):
        """Create a mocked database service."""
        with patch('app.services.database_service.MongoClient'):
            service = DatabaseService()
            service.conversations_collection = MagicMock()
            service.users_collection = MagicMock()
            return service
    
    def test_save_conversation_success(self, mock_db_service):
        """Test saving a conversation successfully."""
        conv = Conversation(
            user_id="user123",
            query="What is AI?",
            plan="Plan",
            research="Research",
            content="Content",
            analysis={},
            final_output="Output",
            data_classification="COMBINED",
            quality_score=0.92,
            quality_level="high"
        )
        
        mock_db_service.conversations_collection.insert_one.return_value = MagicMock(inserted_id="123")
        
        result = mock_db_service.save_conversation(conv)
        
        assert result is True
        mock_db_service.conversations_collection.insert_one.assert_called_once()
    
    def test_save_conversation_no_connection(self):
        """Test saving conversation when not connected."""
        service = DatabaseService()
        service.conversations_collection = None
        
        conv = Conversation(
            user_id="user123",
            query="Test",
            plan="Plan",
            research="Research",
            content="Content",
            analysis={},
            final_output="Output",
            data_classification="COMBINED",
            quality_score=0.8,
            quality_level="high"
        )
        
        result = service.save_conversation(conv)
        assert result is False
    
    def test_get_conversation(self, mock_db_service):
        """Test retrieving a conversation."""
        conv_dict = {
            "user_id": "user123",
            "conversation_id": "conv123",
            "query": "What is AI?",
            "plan": "Plan",
            "research": "Research",
            "content": "Content",
            "analysis": {},
            "final_output": "Output",
            "data_classification": "COMBINED",
            "quality_score": 0.92,
            "quality_level": "high",
            "created_at": datetime.utcnow(),
            "processing_time_seconds": 5.0,
            "tags": []
        }
        
        mock_db_service.conversations_collection.find_one.return_value = conv_dict
        
        result = mock_db_service.get_conversation("conv123")
        
        assert result is not None
        assert isinstance(result, Conversation)
        assert result.conversation_id == "conv123"
        assert result.query == "What is AI?"
    
    def test_get_conversation_not_found(self, mock_db_service):
        """Test retrieving non-existent conversation."""
        mock_db_service.conversations_collection.find_one.return_value = None
        
        result = mock_db_service.get_conversation("nonexistent")
        
        assert result is None
    
    def test_is_connected(self):
        """Test connection status check."""
        service = DatabaseService()
        
        # Not connected
        service.conversations_collection = None
        assert service.is_connected() is False
        
        # Connected
        service.conversations_collection = MagicMock()
        assert service.is_connected() is True
    
    def test_get_db_service_singleton(self):
        """Test that get_db_service returns singleton instance."""
        # This test checks the singleton pattern
        service1 = get_db_service()
        service2 = get_db_service()
        
        assert service1 is service2


class TestDatabaseServiceIntegration:
    """Integration tests for database service (requires MongoDB running)."""
    
    @pytest.mark.skipif(
        os.getenv("MONGODB_URI") is None,
        reason="MongoDB not configured"
    )
    def test_save_and_retrieve_conversation(self):
        """Test saving and retrieving a conversation."""
        service = DatabaseService()
        
        if not service.is_connected():
            pytest.skip("MongoDB not available")
        
        # Create conversation
        conv = Conversation(
            user_id="test_user_" + str(__import__('time').time()),
            query="Integration test query?",
            plan="Test plan",
            research="Test research",
            content="Test content",
            analysis={"test": "data"},
            final_output="Test output",
            data_classification="COMBINED",
            quality_score=0.95,
            quality_level="high"
        )
        
        # Save it
        save_result = service.save_conversation(conv)
        assert save_result is True
        
        # Retrieve it
        retrieved = service.get_conversation(conv.conversation_id)
        assert retrieved is not None
        assert retrieved.query == conv.query
        assert retrieved.user_id == conv.user_id
    
    @pytest.mark.skipif(
        os.getenv("MONGODB_URI") is None,
        reason="MongoDB not configured"
    )
    def test_user_conversation_history(self):
        """Test retrieving user conversation history."""
        service = DatabaseService()
        
        if not service.is_connected():
            pytest.skip("MongoDB not available")
        
        user_id = "test_user_" + str(__import__('time').time())
        
        # Create multiple conversations
        for i in range(3):
            conv = Conversation(
                user_id=user_id,
                query=f"Test query {i}?",
                plan="Plan",
                research="Research",
                content="Content",
                analysis={},
                final_output="Output",
                data_classification="COMBINED",
                quality_score=0.8 + i*0.05,
                quality_level="high"
            )
            service.save_conversation(conv)
        
        # Retrieve history
        history = service.get_user_conversations(user_id, limit=10)
        assert len(history) >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
