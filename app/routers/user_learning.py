from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.services.user_learning import user_learning_service, kg_service, behavior_analyzer
from app.services.memory import memory_service

router = APIRouter(prefix="/users", tags=["user-learning"])


class UserIdRequest(BaseModel):
    user_id: str


@router.post("/profile/{user_id}/learn")
async def learn_from_conversations(user_id: str):
    """Analyze all conversations and build user profile"""
    try:
        # Get all conversations for the user
        conversations = await memory_service.get_all_conversations()
        
        if not conversations:
            raise HTTPException(status_code=404, detail="No conversations found")
        
        # Collect all messages
        all_messages = []
        for conv in conversations:
            for msg in conv.messages:
                all_messages.append((msg.role, msg.content))
        
        # Learn from conversations
        profile = await user_learning_service.learn_from_conversation(
            user_id=user_id,
            messages=all_messages,
            conversation_count=len(conversations)
        )
        
        return {
            "user_id": user_id,
            "profile": profile,
            "message": "User profile updated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get complete user profile"""
    try:
        profile = await user_learning_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}/knowledge-graph")
async def get_user_knowledge_graph(user_id: str):
    """Get user's knowledge graph"""
    try:
        kg = await kg_service.get_knowledge_graph(user_id)
        if not kg:
            raise HTTPException(status_code=404, detail="Knowledge graph not found")
        
        return {
            "user_id": user_id,
            "entities_count": len(kg.entities),
            "relationships_count": len(kg.relationships),
            "top_entities": sorted(kg.entities, key=lambda x: x.frequency, reverse=True)[:10],
            "entities": kg.entities,
            "relationships": kg.relationships
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}/behavior")
async def get_user_behavior(user_id: str):
    """Get user's behavior profile"""
    try:
        behavior = await behavior_analyzer.get_behavior_profile(user_id)
        if not behavior:
            raise HTTPException(status_code=404, detail="Behavior profile not found")
        
        return {
            "user_id": user_id,
            "communication_style": behavior.communication_style,
            "preferred_topics": behavior.preferred_topics,
            "response_length_preference": behavior.response_length_preference,
            "interaction_frequency": behavior.interaction_frequency,
            "patterns": behavior.patterns
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}/context")
async def get_personalized_context(user_id: str):
    """Get personalized context for responding to this user"""
    try:
        context = await user_learning_service.get_personalized_context(user_id)
        
        profile = await user_learning_service.get_user_profile(user_id)
        if not profile:
            context = "User profile not yet built."
        
        return {
            "user_id": user_id,
            "personalized_context": context,
            "recommendation": "Use this context to personalize your response to the user"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/{user_id}/preferences")
async def update_user_preferences(user_id: str, request: dict):
    """Update user preferences"""
    try:
        profile = await user_learning_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found. Learn first.")
        
        # Update preferences
        if "explanation_style" in request:
            profile.preferences.explanation_style = request["explanation_style"]
        
        if "personality_match" in request:
            profile.preferences.personality_match = request["personality_match"]
        
        if "favorite_topics" in request:
            profile.preferences.favorite_topics = request["favorite_topics"]
        
        if "topics_to_avoid" in request:
            profile.preferences.topics_to_avoid = request["topics_to_avoid"]
        
        if "custom_instructions" in request:
            profile.preferences.custom_instructions = request["custom_instructions"]
        
        return {
            "user_id": user_id,
            "message": "Preferences updated",
            "preferences": profile.preferences
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{user_id}/insights")
async def get_user_insights(user_id: str):
    """Get behavioral insights about the user"""
    try:
        profile = await user_learning_service.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        kg = await kg_service.get_knowledge_graph(user_id)
        
        insights = {
            "user_id": user_id,
            "insights": {
                "primary_interests": profile.behavior_profile.preferred_topics[:3],
                "communication_mode": profile.behavior_profile.communication_style,
                "prefers_brief_responses": profile.behavior_profile.response_length_preference == "short",
                "total_concepts_learned": len(kg.entities) if kg else 0,
                "relationship_network_size": len(kg.relationships) if kg else 0,
                "engagement_level": "high" if profile.total_messages > 50 else "medium" if profile.total_messages > 10 else "low"
            },
            "recommendations": [
                f"Tailor responses to {profile.behavior_profile.communication_style} style",
                f"Focus conversations on: {', '.join(profile.behavior_profile.preferred_topics[:2])}",
                f"Use {profile.behavior_profile.response_length_preference} responses",
            ]
        }
        
        return insights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))