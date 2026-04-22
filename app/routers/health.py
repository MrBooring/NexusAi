from fastapi import APIRouter
from app.config.settings import settings

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.app_name, "assistant": settings.assistant_name, "version": settings.version}
