from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EntityType(str, Enum):
    """Types of entities in knowledge graph"""
    PERSON = "person"
    TOPIC = "topic"
    CONCEPT = "concept"
    OBJECT = "object"
    EVENT = "event"
    PLACE = "place"


class RelationType(str, Enum):
    """Types of relationships between entities"""
    RELATED_TO = "related_to"
    CAUSED_BY = "caused_by"
    PART_OF = "part_of"
    SIMILAR_TO = "similar_to"
    OPPOSITE_TO = "opposite_to"
    DEPENDS_ON = "depends_on"
    INFLUENCES = "influences"
    MENTIONS = "mentions"


class Entity(BaseModel):
    """Node in knowledge graph"""
    entity_id: str
    name: str
    type: EntityType
    description: Optional[str] = None
    frequency: int = Field(default=1)  # How many times mentioned
    first_mention: datetime = Field(default_factory=datetime.now)
    last_mention: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Relationship(BaseModel):
    """Edge in knowledge graph"""
    source_id: str
    target_id: str
    relation_type: RelationType
    strength: float = Field(default=1.0, ge=0.0, le=1.0)  # 0-1 confidence
    frequency: int = Field(default=1)
    first_mention: datetime = Field(default_factory=datetime.now)
    last_mention: datetime = Field(default_factory=datetime.now)


class KnowledgeGraph(BaseModel):
    """Complete knowledge graph for a user"""
    user_id: str
    entities: List[Entity] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# Behavior Pattern Models
class BehaviorPattern(BaseModel):
    """A detected behavior pattern"""
    pattern_id: str
    name: str
    description: str
    frequency: int  # How often this pattern occurs
    confidence: float = Field(ge=0.0, le=1.0)  # 0-1 confidence
    triggers: List[str]  # What triggers this behavior
    examples: List[str] = Field(default_factory=list)
    last_observed: datetime = Field(default_factory=datetime.now)


class UserBehaviorProfile(BaseModel):
    """Analysis of user's behavior patterns"""
    user_id: str
    communication_style: str  # formal, casual, technical, etc.
    preferred_topics: List[str] = Field(default_factory=list)
    response_length_preference: str  # short, medium, long
    interaction_frequency: int  # per day
    preferred_time: Optional[str] = None  # morning, afternoon, evening
    emotion_tendency: Optional[str] = None  # positive, neutral, analytical
    patterns: List[BehaviorPattern] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserPreferences(BaseModel):
    """User-defined and learned preferences"""
    user_id: str
    name: Optional[str] = None
    language: str = "en"
    explanation_style: str = "simple"  # simple, detailed, technical
    personality_match: Optional[str] = None  # "helpful", "brief", "creative", etc.
    custom_instructions: Optional[str] = None
    favorite_topics: List[str] = Field(default_factory=list)
    topics_to_avoid: List[str] = Field(default_factory=list)
    learned_preferences: Dict[str, Any] = Field(default_factory=dict)  # Auto-learned
    last_updated: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    """Complete user profile combining all insights"""
    user_id: str
    preferences: UserPreferences
    behavior_profile: UserBehaviorProfile
    knowledge_graph: KnowledgeGraph
    total_conversations: int = 0
    total_messages: int = 0
    interaction_history_days: int = 0
    last_active: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)