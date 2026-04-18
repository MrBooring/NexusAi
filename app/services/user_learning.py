import asyncio
import re
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict, Counter
from app.models.user_learning import (
    Entity, Relationship, KnowledgeGraph, EntityType, RelationType,
    BehaviorPattern, UserBehaviorProfile, UserPreferences, UserProfile
)
from app.services.llm import llm_service
import uuid


class KnowledgeGraphService:
    """Manages knowledge graph construction and entity extraction"""
    
    def __init__(self):
        self.graphs: Dict[str, KnowledgeGraph] = {}
    
    async def extract_entities(self, text: str) -> List[Tuple[str, EntityType]]:
        """Extract entities from text using LLM"""
        try:
            prompt = f"""Extract key entities and their types from this text. Return as JSON array with name and type.
Types: person, topic, concept, object, event, place

Text: {text}

Return JSON array only: [{{"name": "entity", "type": "type"}}]"""
            
            response = await llm_service.generate_response(
                prompt=prompt,
                context="You are an entity extraction expert. Extract only important entities."
            )
            
            # Parse response - handle both valid JSON and text
            entities = []
            import json
            try:
                parsed = json.loads(response)
                for item in parsed:
                    if isinstance(item, dict) and "name" in item and "type" in item:
                        try:
                            entity_type = EntityType(item["type"].lower())
                            entities.append((item["name"], entity_type))
                        except ValueError:
                            entities.append((item["name"], EntityType.CONCEPT))
            except json.JSONDecodeError:
                # Fallback: extract noun phrases
                pass
            
            return entities
        except Exception as e:
            print(f"Entity extraction error: {e}")
            return []
    
    async def extract_relationships(self, text: str, entities: List[str]) -> List[Tuple[str, str, RelationType]]:
        """Extract relationships between entities"""
        try:
            entities_str = ", ".join(entities[:10])  # Limit to first 10
            
            prompt = f"""Find relationships between these entities in the text:
Entities: {entities_str}

Text: {text}

Return JSON array of relationships: [{{"source": "entity1", "target": "entity2", "relation": "related_to"}}]
Relation types: related_to, caused_by, part_of, similar_to, opposite_to, depends_on, influences, mentions"""
            
            response = await llm_service.generate_response(
                prompt=prompt,
                context="Extract only clear, direct relationships."
            )
            
            relationships = []
            import json
            try:
                parsed = json.loads(response)
                for rel in parsed:
                    if all(k in rel for k in ["source", "target", "relation"]):
                        try:
                            rel_type = RelationType(rel["relation"])
                            relationships.append((rel["source"], rel["target"], rel_type))
                        except ValueError:
                            relationships.append((rel["source"], rel["target"], RelationType.RELATED_TO))
            except json.JSONDecodeError:
                pass
            
            return relationships
        except Exception as e:
            print(f"Relationship extraction error: {e}")
            return []
    
    async def build_knowledge_graph(self, user_id: str, conversation_texts: List[str]) -> KnowledgeGraph:
        """Build knowledge graph from conversation texts"""
        if user_id not in self.graphs:
            self.graphs[user_id] = KnowledgeGraph(user_id=user_id)
        
        graph = self.graphs[user_id]
        all_entities = []
        all_relationships = []
        
        # Extract entities and relationships from each message
        for text in conversation_texts:
            entities = await self.extract_entities(text)
            all_entities.extend(entities)
            
            entity_names = [name for name, _ in entities]
            if entity_names:
                relationships = await self.extract_relationships(text, entity_names)
                all_relationships.extend(relationships)
        
        # Add/update entities in graph
        entity_map = {}  # name -> entity_id
        for name, entity_type in all_entities:
            # Check if entity exists
            existing = next((e for e in graph.entities if e.name.lower() == name.lower()), None)
            
            if existing:
                existing.frequency += 1
                existing.last_mention = datetime.now()
                entity_map[name] = existing.entity_id
            else:
                entity_id = str(uuid.uuid4())
                new_entity = Entity(
                    entity_id=entity_id,
                    name=name,
                    type=entity_type
                )
                graph.entities.append(new_entity)
                entity_map[name] = entity_id
        
        # Add/update relationships
        for source, target, rel_type in all_relationships:
            source_id = entity_map.get(source)
            target_id = entity_map.get(target)
            
            if source_id and target_id:
                existing_rel = next(
                    (r for r in graph.relationships 
                     if r.source_id == source_id and r.target_id == target_id and r.relation_type == rel_type),
                    None
                )
                
                if existing_rel:
                    existing_rel.frequency += 1
                    existing_rel.last_mention = datetime.now()
                else:
                    rel = Relationship(
                        source_id=source_id,
                        target_id=target_id,
                        relation_type=rel_type
                    )
                    graph.relationships.append(rel)
        
        graph.updated_at = datetime.now()
        return graph
    
    async def get_knowledge_graph(self, user_id: str) -> Optional[KnowledgeGraph]:
        """Get user's knowledge graph"""
        return self.graphs.get(user_id)


class UserBehaviorAnalyzer:
    """Analyzes user behavior patterns"""
    
    def __init__(self):
        self.behaviors: Dict[str, UserBehaviorProfile] = {}
    
    async def analyze_messages(self, user_id: str, messages: List[Tuple[str, str]]) -> UserBehaviorProfile:
        """Analyze behavioral patterns from messages"""
        if user_id not in self.behaviors:
            self.behaviors[user_id] = UserBehaviorProfile(
                user_id=user_id,
                communication_style="unknown",
                preferred_topics=[],
                response_length_preference="medium"
            )
        
        profile = self.behaviors[user_id]
        
        # Analyze message lengths
        user_messages = [msg for role, msg in messages if role == "user"]
        if user_messages:
            avg_length = sum(len(msg) for msg in user_messages) / len(user_messages)
            if avg_length < 50:
                profile.response_length_preference = "short"
            elif avg_length > 200:
                profile.response_length_preference = "long"
            else:
                profile.response_length_preference = "medium"
        
        # Analyze communication style
        formal_indicators = ["please", "kindly", "moreover", "furthermore", "consequently"]
        casual_indicators = ["hey", "lol", "yeah", "cool", "awesome", "tbh"]
        technical_indicators = ["algorithm", "database", "function", "system", "api", "code"]
        
        text_combined = " ".join(user_messages).lower()
        formal_count = sum(text_combined.count(word) for word in formal_indicators)
        casual_count = sum(text_combined.count(word) for word in casual_indicators)
        technical_count = sum(text_combined.count(word) for word in technical_indicators)
        
        if technical_count > formal_count and technical_count > casual_count:
            profile.communication_style = "technical"
        elif formal_count > casual_count:
            profile.communication_style = "formal"
        elif casual_count > formal_count:
            profile.communication_style = "casual"
        else:
            profile.communication_style = "balanced"
        
        # Extract topics from user messages
        topics = []
        for msg in user_messages[:5]:  # Analyze first few messages
            topic_prompt = f"Extract 1-2 main topics from this message (comma-separated): {msg}"
            try:
                topic_response = await llm_service.generate_response(
                    prompt=topic_prompt,
                    context="Extract concise topics only."
                )
                extracted = [t.strip() for t in topic_response.split(",")]
                topics.extend(extracted)
            except:
                pass
        
        profile.preferred_topics = list(set(topics))[:5]
        profile.updated_at = datetime.now()
        
        return profile
    
    async def get_behavior_profile(self, user_id: str) -> Optional[UserBehaviorProfile]:
        """Get user's behavior profile"""
        return self.behaviors.get(user_id)


class UserLearningService:
    """Combines knowledge graphs and behavior analysis for user modeling"""
    
    def __init__(self):
        self.kg_service = KnowledgeGraphService()
        self.behavior_analyzer = UserBehaviorAnalyzer()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.user_preferences: Dict[str, UserPreferences] = {}
    
    async def learn_from_conversation(self, user_id: str, messages: List[Tuple[str, str]], 
                                     conversation_count: int = 1) -> UserProfile:
        """Learn from a conversation and update user profile"""
        
        # Extract messages for analysis
        message_texts = [msg for _, msg in messages]
        
        # Build/update knowledge graph
        kg = await self.kg_service.build_knowledge_graph(user_id, message_texts)
        
        # Analyze behavior
        behavior_profile = await self.behavior_analyzer.analyze_messages(user_id, messages)
        
        # Create/update user preferences
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)
        
        prefs = self.user_preferences[user_id]
        
        # Learn preferences from communication style
        if behavior_profile.communication_style == "technical":
            prefs.explanation_style = "technical"
        elif behavior_profile.communication_style == "formal":
            prefs.explanation_style = "detailed"
        else:
            prefs.explanation_style = "simple"
        
        # Update favorite topics
        prefs.favorite_topics = behavior_profile.preferred_topics
        
        # Create complete user profile
        profile = UserProfile(
            user_id=user_id,
            preferences=prefs,
            behavior_profile=behavior_profile,
            knowledge_graph=kg,
            total_conversations=conversation_count,
            total_messages=len(messages)
        )
        
        self.user_profiles[user_id] = profile
        return profile
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get complete user profile"""
        return self.user_profiles.get(user_id)
    
    async def get_personalized_context(self, user_id: str) -> str:
        """Get personalized context for responding to user"""
        profile = await self.get_user_profile(user_id)
        if not profile:
            return ""
        
        context_parts = []
        
        # Add communication style hint
        if profile.behavior_profile.communication_style:
            context_parts.append(f"User prefers {profile.behavior_profile.communication_style} communication style.")
        
        # Add explanation style
        context_parts.append(f"Explain using {profile.preferences.explanation_style} level.")
        
        # Add topic preferences
        if profile.behavior_profile.preferred_topics:
            topics = ", ".join(profile.behavior_profile.preferred_topics[:3])
            context_parts.append(f"User is interested in: {topics}")
        
        # Add response length preference
        context_parts.append(f"Preferred response length: {profile.behavior_profile.response_length_preference}")
        
        return " ".join(context_parts)


# Global services
kg_service = KnowledgeGraphService()
behavior_analyzer = UserBehaviorAnalyzer()
user_learning_service = UserLearningService()