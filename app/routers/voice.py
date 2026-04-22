import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config.settings import settings
from app.services.llm import llm_service
from app.services.memory import memory_service
from app.services.user_learning import user_learning_service
from app.services.voice import voice_service

router = APIRouter(prefix="/voice", tags=["voice"])


class SpeakRequest(BaseModel):
    text: str


def _build_context(conversation) -> str:
    context_messages = conversation.messages[:-1][-settings.max_chat_context_messages:]
    conversation_context = "\n".join(
        f"{msg.role}: {msg.content}"
        for msg in context_messages
    )
    if len(conversation_context) > settings.max_chat_context_chars:
        conversation_context = conversation_context[-settings.max_chat_context_chars:]
    return conversation_context


@router.get("/status")
async def get_voice_status():
    try:
        return await voice_service.get_status()
    except Exception as e:
        # Return status with error message rather than crashing
        return {
            "whisper_installed": False,
            "tts_installed": False,
            "whisper_model": settings.whisper_model,
            "tts_model": settings.tts_model,
            "error": str(e)
        }


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        transcript = await voice_service.transcribe_audio_bytes(audio_bytes, file.filename)
        return {"transcript": transcript}
    except Exception as e:
        print(f"Transcribe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/speak")
async def speak_text(request: SpeakRequest):
    try:
        audio = await voice_service.synthesize_speech(request.text)
        return audio
    except Exception as e:
        print(f"Speak error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/respond")
async def voice_respond(
    file: UploadFile = File(...),
    conversation_id: Optional[str] = Form(default=None),
):
    try:
        audio_bytes = await file.read()
        transcript = await voice_service.transcribe_audio_bytes(audio_bytes, file.filename)
        if not transcript:
            raise HTTPException(status_code=400, detail="No speech detected in audio.")

        if not conversation_id:
            conversation_id = await memory_service.create_conversation(
                title="Voice Chat",
                metadata={"source": "voice_chat"}
            )

        conversation = await memory_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=transcript
        )

        conversation_context = _build_context(conversation)
        
        # Ensure user profile exists - don't fail if this has errors
        try:
            await memory_service.ensure_user_profile("local_user")
        except Exception as e:
            print(f"Warning: Failed to ensure user profile: {e}")
        
        # Get personalized context - don't fail if this has errors
        personalized_context = None
        try:
            personalized_context = await user_learning_service.get_response_guidance("local_user")
        except Exception as e:
            print(f"Warning: Failed to get personalized context: {e}")
        
        if personalized_context:
            conversation_context = f"{personalized_context}\n\nRecent conversation:\n{conversation_context}"

        response_text = await llm_service.generate_response(
            prompt=transcript,
            context=conversation_context
        )

        conversation = await memory_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_text
        )

        audio_url = None
        tts_error = None
        try:
            audio = await voice_service.synthesize_speech(response_text)
            audio_url = audio["audio_url"]
        except Exception as e:
            tts_error = str(e)
            print(f"TTS error: {tts_error}")

        return {
            "conversation_id": conversation_id,
            "transcript": transcript,
            "response": response_text,
            "audio_url": audio_url,
            "tts_error": tts_error,
            "messages_count": len(conversation.messages),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Voice respond error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    try:
        safe_name = os.path.basename(filename)
        path = Path("./data/audio") / safe_name
        if not path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        return FileResponse(path, media_type="audio/wav", filename=safe_name)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
