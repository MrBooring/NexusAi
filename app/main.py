from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from app.routers.health import router as health_router
from app.routers.llm import router as llm_router
from app.routers.memory import router as memory_router
from app.routers.user_learning import router as user_learning_router
import os

app = FastAPI(
    title="NexusAI",
    description="A fully local, privacy-first personal AI assistant",
    version="0.2.0"
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

@app.get("/")
def read_root():
    return {"message": "Welcome to NexusAI - Local AI Assistant", "version": "0.2.0"}

@app.get("/dashboard")
def get_dashboard():
    """Serve the dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dashboard.html")
    return FileResponse(dashboard_path, media_type="text/html")