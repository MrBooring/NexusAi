# NexusAI - Local AI Assistant

Version 0.1.0 - First Usable Milestone

## Overview

NexusAI is a fully local, privacy-first personal AI assistant that runs entirely on your hardware with no cloud dependencies.

## Features (0.1)

- ✅ FastAPI backend setup
- ✅ Basic API endpoints (`/` and `/health`)
- ✅ Auto-generated API documentation at `/docs`
- ✅ Project structure ready for expansion

## Quick Start

1. Activate virtual environment:

   ```bash
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the development server:

   ```bash
   fastapi dev main.py
   ```

4. Test the API:
   - Open http://localhost:8000/ in your browser
   - Check health at http://localhost:8000/health
   - View API docs at http://localhost:8000/docs

## Next Steps

This 0.1 release provides a solid foundation for:

- Voice processing integration (Whisper, Coqui TTS)
- Local LLM integration (Ollama)
- Memory system (ChromaDB)
- Multi-device support
- Plugin architecture

## Architecture

- `main.py`: FastAPI application entry point
- `requirements.txt`: Python dependencies
- `docs/`: Project documentation
- `.github/agents/`: Custom development agents
