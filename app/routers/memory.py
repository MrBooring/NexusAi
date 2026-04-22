from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.memory import memory_service
from app.services.llm import llm_service
from app.config.settings import settings
from app.services.user_learning import user_learning_service
from app.models.conversation import (
    Conversation, ConversationRequest, ConversationResponse, 
    SearchRequest, Message
)

router = APIRouter(prefix="/memory", tags=["memory"])


class CreateConversationRequest(BaseModel):
    title: Optional[str] = None
    metadata: Optional[dict] = None


class AddMessageRequest(BaseModel):
    message: str


@router.post("/conversations/create")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation"""
    try:
        conversation_id = await memory_service.create_conversation(
            title=request.title,
            metadata=request.metadata
        )
        return {"conversation_id": conversation_id, "message": "Conversation created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation"""
    try:
        conversation = await memory_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations")
async def list_conversations():
    """List all conversations"""
    try:
        conversations = await memory_service.get_all_conversations()
        return {"conversations": conversations, "count": len(conversations)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, request: AddMessageRequest):
    """Add a user message to conversation and get LLM response"""
    try:
        # Add user message
        conversation = await memory_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # Get LLM response based on conversation context
        context_messages = conversation.messages[:-1][-settings.max_chat_context_messages:]
        conversation_context = "\n".join([
            f"{msg.role}: {msg.content}"
            for msg in context_messages
        ])
        if len(conversation_context) > settings.max_chat_context_chars:
            conversation_context = conversation_context[-settings.max_chat_context_chars:]

        await memory_service.ensure_user_profile("local_user")
        personalized_context = await user_learning_service.get_response_guidance("local_user")
        if personalized_context:
            conversation_context = f"{personalized_context}\n\nRecent conversation:\n{conversation_context}"
        
        llm_response = await llm_service.generate_response(
            prompt=request.message,
            context=conversation_context
        )
        
        # Add assistant response to conversation
        conversation = await memory_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=llm_response
        )
        
        return {
            "conversation_id": conversation_id,
            "user_message": request.message,
            "assistant_response": llm_response,
            "messages_count": len(conversation.messages)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_conversations(request: SearchRequest):
    """Search conversations by semantic similarity"""
    try:
        results = await memory_service.search_conversations(
            query=request.query,
            limit=request.limit
        )
        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{conversation_id}/summary")
async def get_conversation_summary(conversation_id: str):
    """Get a summary of a conversation"""
    try:
        conversation = await memory_service.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        summary = await memory_service.get_conversation_summary(conversation_id)
        return {
            "conversation_id": conversation_id,
            "summary": summary,
            "message_count": len(conversation.messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_memory_stats():
    """Get comprehensive memory system statistics"""
    try:
        stats = await memory_service.get_memory_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/advanced")
async def advanced_search(request: SearchRequest):
    """Advanced search with filters"""
    try:
        results = await memory_service.search_conversations_advanced(
            query=request.query,
            limit=request.limit,
            min_importance=request.min_importance,
            topics=request.topics
        )
        return {
            "query": request.query,
            "filters": {
                "min_importance": request.min_importance,
                "topics": request.topics
            },
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/{topic}")
async def get_conversations_by_topic(topic: str, limit: int = 10):
    """Get conversations containing a specific topic"""
    try:
        conversations = await memory_service.get_conversations_by_topic(topic, limit)
        return {
            "topic": topic,
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_conversations(limit: int = 5):
    """Get most recently active conversations"""
    try:
        conversations = await memory_service.get_recent_conversations(limit)
        return {
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/important")
async def get_important_conversations(limit: int = 5):
    """Get most important conversations by score"""
    try:
        conversations = await memory_service.get_important_conversations(limit)
        return {
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
