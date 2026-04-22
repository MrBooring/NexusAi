# Friday - Local AI Assistant

Version 0.6.0 - Local Assistant MVP Foundation

## Overview

Friday is a fully local, privacy-first personal AI assistant that runs on your own hardware with no cloud dependency.

## Current Capabilities

- FastAPI backend with docs at `/docs`
- Local LLM chat via Ollama
- Persistent conversation memory
- Semantic and fallback search across conversations
- User profile learning and personalized responses
- Dashboard for conversations, search, profiles, voice interaction, and device visibility
- Voice API surface for transcription, response generation, and speech output
- Lightweight multi-device hub with REST status and WebSocket connections

## Quick Start

1. Activate the virtual environment:

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

4. Open:
   - API root: http://localhost:8000/
   - Health: http://localhost:8000/health
   - Docs: http://localhost:8000/docs
   - Dashboard: http://localhost:8000/dashboard

## Main Routes

- `/llm/*` - local model chat and model status
- `/memory/*` - conversation storage, retrieval, search, and analytics
- `/users/*` - learned profile, behavior, graph, and personalization
- `/voice/*` - voice status, transcription, speech synthesis, and voice chat
- `/devices/*` - device status and multi-device WebSocket hub

## What Still Needs Work

- Live streaming voice instead of request/response audio uploads
- Real device clients beyond the dashboard and raw WebSocket endpoint
- Command/plugin execution for automation and home tasks
- Stronger automated test coverage for API workflows
- Long-run stability checks and performance tuning on real hardware

## Architecture

- `app/main.py` - FastAPI application setup
- `app/routers/` - REST and WebSocket routes
- `app/services/` - LLM, memory, voice, learning, and device hub services
- `app/models/` - Pydantic data models
- `docs/` - project documentation
- `dashboard.html` - local web dashboard
