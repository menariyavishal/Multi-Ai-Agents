"""Database service for SQLite and MongoDB operations."""

import sqlite3
import uuid
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv
from app.core.logger import get_logger

logger = get_logger(__name__)

# Load environment
load_dotenv()

# SQLite path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "app.db"

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "neuro_agents"


class DatabaseService:
    """Service for database operations (SQLite for users/keys, MongoDB for responses)."""
    
    def __init__(self):
        """Initialize database service."""
        self.db_path = DB_PATH
        self.mongo_uri = MONGO_URI
        self._mongo_client = None
        self._mongo_db = None
        logger.info("DatabaseService initialized")
    
    def _get_sqlite_connection(self) -> sqlite3.Connection:
        """Get SQLite connection."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}. Run init_sqlite.py first.")
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_mongo_db(self):
        """Get MongoDB database connection (lazy init)."""
        if self._mongo_db is None:
            try:
                self._mongo_client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
                self._mongo_client.admin.command('ping')
                self._mongo_db = self._mongo_client[DB_NAME]
                logger.info("Connected to MongoDB")
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"MongoDB not available: {str(e)}")
                return None
        
        return self._mongo_db
    
    # ===== USER MANAGEMENT =====
    
    def register_user(self, username: str, email: str, password_hash: str) -> Optional[str]:
        """Register a new user and generate API key.
        
        Args:
            username: Username (unique)
            email: Email address (unique)
            password_hash: Hashed password
        
        Returns:
            Generated API key if successful, None if error
        """
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            
            # Generate IDs
            user_id = str(uuid.uuid4())
            api_key = f"sk_{uuid.uuid4().hex[:32]}"
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (user_id, username, email, password_hash)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, email, password_hash))
            
            # Insert API key
            cursor.execute("""
                INSERT INTO api_keys (key_id, user_id, api_key, name)
                VALUES (?, ?, ?, ?)
            """, (str(uuid.uuid4()), user_id, api_key, f"Default key for {username}"))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User registered: {username} ({user_id})")
            return api_key
        
        except sqlite3.IntegrityError as e:
            logger.warning(f"User registration failed (duplicate): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return user_id.
        
        Args:
            api_key: API key to validate
        
        Returns:
            user_id if valid, None if invalid or inactive
        """
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_id FROM api_keys
                WHERE api_key = ? AND is_active = 1
            """, (api_key,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.info(f"API key validated: {api_key[:10]}...")
                return row['user_id']
            
            logger.warning(f"Invalid API key: {api_key[:10]}...")
            return None
        
        except Exception as e:
            logger.error(f"API key validation failed: {str(e)}")
            return None
    
    # ===== QUERY HISTORY =====
    
    def save_query_history(
        self,
        user_id: str,
        query_text: str,
        session_id: Optional[str] = None,
        agent_outputs: Optional[Dict[str, Any]] = None,
        status: str = "completed",
        error_message: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        iterations_used: Optional[int] = None,
        quality_score: Optional[float] = None
    ) -> Optional[str]:
        """Save query to history.
        
        Args:
            user_id: User ID
            query_text: The query text
            session_id: Session ID
            agent_outputs: Output from agents (as dict)
            status: Query status (completed, failed, etc.)
            error_message: Error message if failed
            execution_time_seconds: How long it took
            iterations_used: Number of iterations
            quality_score: Quality score from reviewer
        
        Returns:
            query_id if successful, None if error
        """
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            
            query_id = str(uuid.uuid4())
            query_hash = str(hash(query_text.lower()))
            agent_outputs_json = json.dumps(agent_outputs) if agent_outputs else None
            
            cursor.execute("""
                INSERT INTO query_history (
                    query_id, user_id, session_id, query_text, query_hash,
                    agent_outputs, status, error_message, execution_time_seconds,
                    iterations_used, quality_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                query_id, user_id, session_id, query_text, query_hash,
                agent_outputs_json, status, error_message, execution_time_seconds,
                iterations_used, quality_score
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Query saved: {query_id[:8]}... for user {user_id[:8]}...")
            return query_id
        
        except Exception as e:
            logger.error(f"Failed to save query history: {str(e)}")
            return None
    
    def get_history(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get query history for a user (paginated).
        
        Args:
            user_id: User ID
            limit: Number of records to return
            offset: Number of records to skip
        
        Returns:
            List of query history records
        """
        try:
            conn = self._get_sqlite_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM query_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset))
            
            rows = cursor.fetchall()
            conn.close()
            
            # Convert to dicts
            history = []
            for row in rows:
                record = dict(row)
                # Parse JSON if present
                if record.get('agent_outputs'):
                    try:
                        record['agent_outputs'] = json.loads(record['agent_outputs'])
                    except:
                        pass
                history.append(record)
            
            logger.info(f"Retrieved {len(history)} history records for user {user_id[:8]}...")
            return history
        
        except Exception as e:
            logger.error(f"Failed to get history: {str(e)}")
            return []
    
    # ===== MONGODB OPERATIONS =====
    
    def save_full_state_to_mongo(
        self,
        session_id: str,
        query: str,
        workflow_state: Dict[str, Any],
        user_id: Optional[str] = None,
        final_answer: Optional[str] = None,
        execution_time_seconds: Optional[float] = None,
        status: str = "completed"
    ) -> bool:
        """Save complete workflow state to MongoDB.
        
        Args:
            session_id: Unique session ID
            query: User query
            workflow_state: Full LangGraph state dict
            user_id: Optional user ID
            final_answer: Final answer/response
            execution_time_seconds: Execution time
            status: Execution status
        
        Returns:
            True if successful, False otherwise
        """
        try:
            db = self._get_mongo_db()
            if db is None:
                logger.warning("MongoDB not available, skipping state storage")
                return False
            
            document = {
                "session_id": session_id,
                "query": query,
                "workflow_state": workflow_state,
                "user_id": user_id,
                "final_answer": final_answer,
                "execution_time_seconds": execution_time_seconds,
                "status": status,
                "timestamp": datetime.utcnow()
            }
            
            result = db.agent_responses.insert_one(document)
            
            logger.info(f"Workflow state saved to MongoDB: {session_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save workflow state to MongoDB: {str(e)}")
            return False
    
    def get_full_state_from_mongo(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve complete workflow state from MongoDB.
        
        Args:
            session_id: Session ID to retrieve
        
        Returns:
            Workflow state dict if found, None otherwise
        """
        try:
            db = self._get_mongo_db()
            if db is None:
                logger.warning("MongoDB not available")
                return None
            
            document = db.agent_responses.find_one({"session_id": session_id})
            
            if document:
                # Remove MongoDB ID field
                document.pop("_id", None)
                logger.info(f"Retrieved workflow state from MongoDB: {session_id}")
                return document
            
            logger.warning(f"Workflow state not found: {session_id}")
            return None
        
        except Exception as e:
            logger.error(f"Failed to retrieve workflow state: {str(e)}")
            return None
    
    def close(self):
        """Close database connections."""
        if self._mongo_client:
            self._mongo_client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_db_service() -> DatabaseService:
    """Get or create global DatabaseService instance.
    
    Returns:
        DatabaseService instance
    """
    global _db_service
    
    if _db_service is None:
        _db_service = DatabaseService()
    
    return _db_service
