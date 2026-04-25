"""MongoDB Models for conversation history and user profiles."""

from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ConversationMessage(BaseModel):
    """Individual message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    """MongoDB conversation document."""
    user_id: str  # Unique user identifier
    conversation_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    title: Optional[str] = None  # Auto-generated from first query
    query: str  # The user's original question
    
    # Agent responses
    plan: str = ""  # Planner's comprehensive plan
    research: str = ""  # Researcher's gathered data and analysis
    content: str = ""  # Final content/answer
    analysis: Dict[str, Any] = Field(default_factory=dict)  # Analyst's insights
    final_output: str = ""  # Writer's final output
    
    # Metadata
    data_classification: str = "COMBINED"  # REAL_TIME, HISTORICAL, COMBINED
    quality_score: float = 0.0  # 0.0 - 1.0
    quality_level: str = "medium"  # high, medium, low
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time_seconds: Optional[float] = None
    
    # Tags for searching
    tags: List[str] = []  # e.g., ["weather", "current", "india"]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserProfile(BaseModel):
    """MongoDB user profile document."""
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # User preferences
    preferred_data_classification: str = "COMBINED"  # Default data type
    theme: str = "light"  # UI theme preference
    
    # Statistics
    total_conversations: int = 0
    total_queries: int = 0
    average_quality_score: float = 0.0
    
    # Last activity
    last_query_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationSummary(BaseModel):
    """Summary of conversation for listing."""
    conversation_id: str
    title: str
    query: str
    created_at: datetime
    data_classification: str
    quality_score: float
    processing_time_seconds: Optional[float] = None
    final_output: str = ""
