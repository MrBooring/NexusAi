## Project Overview

## What is Friday?

Friday is a fully local, privacy-first personal AI assistant inspired by the idea of a home "brain" server. It keeps conversations, learning, and voice processing on local hardware rather than depending on cloud APIs.

## Vision

Build an assistant that:

- understands text and voice requests
- learns preferences and adapts responses over time
- keeps memory and processing local
- can serve multiple devices through a central backend
- grows into an extensible platform for plugins and automation

## What Is Working Now

### Voice Interaction

- voice endpoints for transcription, speech output, and voice-chat orchestration
- dashboard voice panel for recording/uploading audio and playing replies
- lazy-loaded Whisper and Coqui integration with dependency checks

### Intelligent Processing

- local LLM chat through Ollama
- persistent memory with conversation summaries, topics, and search
- learned user profile with communication style, preferred length, and topic interests
- personalized responses based on the current user profile

### Multi-Device Foundation

- device hub REST API for status and recent activity
- WebSocket endpoint for connecting device agents
- dashboard view of connected devices and device activity

### Privacy First

- local-only architecture
- local data persistence
- no required API keys

## Current Phase

**Current Phase**: MVP Foundation / Local Assistant Core

The project has moved beyond architecture-only planning. The core assistant stack now exists, but it still needs production hardening and real client/device polish.

## Next Milestones

1. Real device clients using the WebSocket device hub
2. Streaming voice interaction for lower-latency speech UX
3. Command/plugin execution for practical assistant tasks
4. Better automated tests and stability checks
5. Performance tuning toward reliable sub-2-second local responses

## Success Criteria Status

- [x] Brain server can process text input and generate local responses
- [x] Brain server has a voice processing API surface
- [x] Learned profiles can personalize responses
- [x] Multi-device communication foundation exists through WebSockets
- [ ] At least 2 real device clients connect and communicate reliably
- [ ] Assistant handles 10+ real-world commands end to end
- [ ] Response time is under 2 seconds for most real workloads
- [ ] System runs stably for 24+ hours without restart

---

**Last Updated**: April 20, 2026
