from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.llm import llm_service
from app.services.memory import memory_service
from app.config.settings import settings
from app.services.user_learning import user_learning_service

router = APIRouter(prefix="/llm", tags=["llm"])


class ChatRequest(BaseModel):
    prompt: str
    context: str = ""
    conversation_id: Optional[str] = None


@router.get("/status")
async def get_llm_status():
    """Check Ollama status and available models"""
    try:
        status = await llm_service.check_ollama_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List available Ollama models"""
    try:
        models = await llm_service.list_available_models()
        return {"models": models}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_llm(request: ChatRequest):
    """Generate a response from the LLM and persist conversation memory."""
    try:
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = await memory_service.create_conversation(
                title="LLM Chat",
                metadata={"source": "llm_chat"}
            )

        await memory_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.prompt
        )

        await memory_service.ensure_user_profile("local_user")
        personalized_context = await user_learning_service.get_response_guidance("local_user")
        context = request.context[-settings.max_chat_context_chars:]
        if personalized_context:
            context = f"{personalized_context}\n\n{context}"

        response = await llm_service.generate_response(
            prompt=request.prompt,
            context=context
        )

        await memory_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response
        )

        return {"conversation_id": conversation_id, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
