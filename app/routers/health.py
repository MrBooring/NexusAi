from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "NexusAI", "version": "0.1.0"}