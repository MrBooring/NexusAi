from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from app.routers.health import router as health_router
from app.routers.llm import router as llm_router
from app.routers.memory import router as memory_router
from app.routers.user_learning import router as user_learning_router
from app.routers.devices import router as devices_router
from app.routers.voice import router as voice_router
from app.config.settings import settings
import os

app = FastAPI(
    title=settings.app_name,
    description="A fully local, privacy-first personal AI assistant",
    version=settings.version
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(llm_router)
app.include_router(memory_router)
app.include_router(user_learning_router)
app.include_router(devices_router)
app.include_router(voice_router)

@app.get("/")
def read_root():
    jarvis_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jarvis.html")
    return FileResponse(jarvis_path, media_type="text/html")

@app.get("/dashboard")
def get_dashboard():
    """Serve the dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard.html")
    return FileResponse(dashboard_path, media_type="text/html")
