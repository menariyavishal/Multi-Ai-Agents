"""MongoDB Database Service for storing and retrieving conversations."""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.models.conversation import Conversation, UserProfile, ConversationSummary
from app.core.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service for MongoDB operations - conversation history and user profiles."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
        self.mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/nueuro_agents")
        self.db_name = os.getenv("MONGODB_DB_NAME", "nueuro_agents")
        self.client = None
        self.db = None
        self.conversations_collection = None
        self.users_collection = None
        self._connect()
    
    def _connect(self) -> bool:
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            
            # Get or create collections
            self.conversations_collection = self.db["conversations"]
            self.users_collection = self.db["users"]
            
            # Create indexes for faster queries
            self._create_indexes()
            
            logger.info(f"Connected to MongoDB: {self.db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            logger.warning("Using in-memory storage (conversations will not persist)")
            return False
    
    def _create_indexes(self):
        """Create MongoDB indexes for optimized queries."""
        try:
            # Check if collections are available
            if self.conversations_collection is None or self.users_collection is None:
                logger.warning("Cannot create indexes - MongoDB collections not available")
                return
            
            # Index for finding conversations by user_id and created_at
            self.conversations_collection.create_index([("user_id", DESCENDING), ("created_at", DESCENDING)])
            
            # Index for finding conversations by conversation_id
            self.conversations_collection.create_index("conversation_id", unique=True)
            
            # Index for user profiles
            self.users_collection.create_index("user_id", unique=True)
            self.users_collection.create_index("email", unique=True, sparse=True)
            
            logger.info("MongoDB indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {str(e)}")
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """Save a new conversation to MongoDB."""
        try:
            if self.conversations_collection is None:
                logger.warning("MongoDB not connected - conversation not saved")
                return False
            
            conv_dict = conversation.dict()
            result = self.conversations_collection.insert_one(conv_dict)
            
            logger.info(f"Conversation saved: {conversation.conversation_id}")
            
            # Update user stats
            self._update_user_stats(conversation.user_id, conversation.quality_score)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}")
            return False
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a single conversation by ID."""
        try:
            if self.conversations_collection is None:
                return None
            
            doc = self.conversations_collection.find_one({"conversation_id": conversation_id})
            if doc:
                doc.pop("_id", None)  # Remove MongoDB internal ID
                return Conversation(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving conversation: {str(e)}")
            return None
    
    def get_user_conversations(self, user_id: str, limit: int = 20, skip: int = 0) -> List[ConversationSummary]:
        """Get all conversations for a user (paginated)."""
        try:
            if self.conversations_collection is None:
                return []
            
            # Query conversations sorted by newest first
            conversations = self.conversations_collection.find(
                {"user_id": user_id}
            ).sort("created_at", DESCENDING).skip(skip).limit(limit)
            
            summaries = []
            for conv in conversations:
                conv.pop("_id", None)
                # Auto-generate title from first 50 chars of query if not provided
                title = conv.get("title") or f"{conv.get('query', 'Query')[:50]}..."
                summary = ConversationSummary(
                    conversation_id=conv["conversation_id"],
                    title=title,
                    query=conv["query"],
                    created_at=conv["created_at"],
                    data_classification=conv["data_classification"],
                    quality_score=conv["quality_score"],
                    processing_time_seconds=conv.get("processing_time_seconds"),
                    final_output=conv.get("final_output", "")
                )
                summaries.append(summary)
            
            logger.info(f"Retrieved {len(summaries)} conversations for user {user_id}")
            return summaries
            
        except Exception as e:
            logger.error(f"Error retrieving user conversations: {str(e)}")
            return []
    
    def search_conversations(self, user_id: str, query: str, limit: int = 10) -> List[ConversationSummary]:
        """Search conversations by query text or tags."""
        try:
            if self.conversations_collection is None:
                return []
            
            # Search in query, plan, content, and tags
            conversations = self.conversations_collection.find(
                {
                    "user_id": user_id,
                    "$or": [
                        {"query": {"$regex": query, "$options": "i"}},
                        {"content": {"$regex": query, "$options": "i"}},
                        {"tags": {"$regex": query, "$options": "i"}}
                    ]
                }
            ).sort("created_at", DESCENDING).limit(limit)
            
            summaries = []
            for conv in conversations:
                conv.pop("_id", None)
                title = conv.get("title") or f"{conv.get('query', 'Query')[:50]}..."
                summary = ConversationSummary(
                    conversation_id=conv["conversation_id"],
                    title=title,
                    query=conv["query"],
                    created_at=conv["created_at"],
                    data_classification=conv["data_classification"],
                    quality_score=conv["quality_score"],
                    processing_time_seconds=conv.get("processing_time_seconds")
                )
                summaries.append(summary)
            
            logger.info(f"Found {len(summaries)} matching conversations for user {user_id}")
            return summaries
            
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []
    
    def create_user(self, user_profile: UserProfile) -> bool:
        """Create a new user profile."""
        try:
            if self.users_collection is None:
                return False
            
            # Do not persist null fields into MongoDB.
            # The unique email index should only apply to real email values,
            # not auto-created stats profiles that do not have an email yet.
            user_dict = user_profile.dict(exclude_none=True)
            result = self.users_collection.insert_one(user_dict)
            
            logger.info(f"User created: {user_profile.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return False
    
    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile."""
        try:
            if self.users_collection is None:
                return None
            
            doc = self.users_collection.find_one({"user_id": user_id})
            if doc:
                doc.pop("_id", None)
                return UserProfile(**doc)
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            return None
    
    def _update_user_stats(self, user_id: str, quality_score: float):
        """Update user statistics after saving conversation."""
        try:
            if self.users_collection is None:
                return
            
            user = self.get_user(user_id)
            if user:
                # Update existing user
                new_avg = (user.average_quality_score * user.total_conversations + quality_score) / (user.total_conversations + 1)
                self.users_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "total_conversations": user.total_conversations + 1,
                            "total_queries": user.total_queries + 1,
                            "average_quality_score": new_avg,
                            "last_query_at": datetime.utcnow()
                        }
                    }
                )
            else:
                # Create new user profile
                new_user = UserProfile(
                    user_id=user_id,
                    total_conversations=1,
                    total_queries=1,
                    average_quality_score=quality_score
                )
                self.create_user(new_user)
                
        except Exception as e:
            logger.warning(f"Error updating user stats: {str(e)}")
    
    def get_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            user = self.get_user(user_id)
            if user:
                return {
                    "total_conversations": user.total_conversations,
                    "total_queries": user.total_queries,
                    "average_quality_score": user.average_quality_score,
                    "last_query_at": user.last_query_at
                }
            return {}
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {}
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        return self.conversations_collection is not None


# Global database instance
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get or create database service instance."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
