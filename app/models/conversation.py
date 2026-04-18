from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Message(BaseModel):
    """Single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Conversation(BaseModel):
    """A conversation session with multiple messages"""
    conversation_id: str
    title: Optional[str] = None
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)  # Store context, device info, etc.
    summary: Optional[str] = None  # Auto-generated summary
    topics: List[str] = Field(default_factory=list)  # Extracted topics
    importance_score: float = Field(default=1.0)  # 0-1 scale of importance
    message_count: int = Field(default=0)
    last_activity: datetime = Field(default_factory=datetime.now)


class ConversationRequest(BaseModel):
    """Request to add a message to conversation"""
    conversation_id: str
    prompt: str
    context: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response with conversation data"""
    conversation_id: str
    title: Optional[str] = None
    messages: List[Message]
    created_at: datetime
    updated_at: datetime
    summary: Optional[str] = None
    topics: List[str] = []
    importance_score: float = 1.0
    message_count: int = 0


class SearchRequest(BaseModel):
    """Request to search conversations"""
    query: str
    limit: int = 5
    min_importance: float = 0.0
    topics: Optional[List[str]] = None  # Filter by topics


class MemoryStats(BaseModel):
    """Memory system statistics"""
    total_conversations: int
    total_messages: int
    average_conversation_length: float
    oldest_conversation: Optional[datetime]
    newest_conversation: Optional[datetime]
    top_topics: List[dict]  # [{"topic": "name", "count": 5}, ...]
    storage_size_mb: float