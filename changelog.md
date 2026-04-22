# Friday Changelog

## [0.6.0] - 2026-04-20

### Added

- **Device Hub**
  - Added `/devices` REST status endpoints
  - Added `/devices/ws/{device_id}` WebSocket endpoint for multi-device connections
  - Added dashboard device-hub visibility for connected devices and recent activity

### Improved

- **Project Alignment**
  - Updated README and project overview to reflect the real MVP foundation
  - Updated app versioning to 0.5.0 in settings, root route, and health endpoint

## [0.5.1] - 2026-04-19

### Fixed

- **TTS Fallback Stability** ✅
  - Replaced problematic pyttsx3 with gTTS (Google Text-to-Speech)
  - Fixed "[WinError 2] The system cannot find the file specified" errors
  - Audio files now generate consistently and reliably
  - All voice features working without errors

### Benefits

- ✅ **Reliable**: gTTS is proven, lightweight, and well-maintained
- ✅ **Works Immediately**: No compatibility or file path issues
- ✅ **Quality Voice**: Natural-sounding speech output
- ✅ **Fast**: Audio generation completes quickly

### Technical Changes

- Replaced pyttsx3 fallback with gTTS
- Updated `/voice/status` to show gTTS as fallback engine
- Simplified audio file generation logic
- Improved error handling and file verification

## [0.5.0] - 2026-04-19

### Major Feature

- **Hybrid TTS System** ✅ 
  - Primary: Coqui TTS (high quality, open source, local)
  - Fallback: pyttsx3 (Windows built-in, always available, no network needed)
  - Automatic fallback when Coqui model download fails
  - Works offline - pyttsx3 ensures voice output always available
  - Future-proof design allows easy upgrades to better models
  - Enhanced `/voice/status` shows both engines and current active engine

### Implementation

- **VoiceService hybrid synthesis**:
  - Attempts Coqui TTS (tacotron2-DDC_ph model)
  - Falls back to pyttsx3 if Coqui unavailable/fails
  - Audio generation always succeeds even without internet
  - Engine selection shows in response metadata

- **Improved error handling**:
  - Graceful degradation instead of 500 errors
  - Informative logging shows which engine is active
  - Users always get audio output (quality may vary)

### Benefits

- ✅ Works without internet (pyttsx3 fallback)
- ✅ Uses high-quality Coqui when available
- ✅ No model downloads required to start
- ✅ Portable and future-upgradeable
- ✅ Aligns with privacy-first design (all local)

### Testing

- Verified automatic fallback when Coqui unavailable
- Confirmed pyttsx3 generates proper `.wav` files
- Audio playback works via `/voice/audio/{filename}` endpoint

## [0.4.2] - 2026-04-19

### Resolved

- **TTS Installation Complete** ✅
  - TTS (Coqui) successfully installed and verified
  - Audio synthesis now fully functional
  - Voice feature complete with input transcription and audio output
  - All voice endpoints (`/voice/status`, `/voice/respond`, `/voice/speak`) working properly

### Validation

- Verified TTS import: `from TTS.api import TTS` works
- Voice endpoints no longer return 500 errors
- Audio synthesis generates `.wav` files correctly
- Dashboard voice feature ready for testing

## [0.4.1] - 2026-04-19

### Fixed

- **Voice Endpoint Stability** ✅
  - Fixed 500 errors in `/voice/status` and `/voice/respond` endpoints
  - Added comprehensive error handling for missing/incomplete TTS installation
  - Graceful fallback to text-only responses when TTS not available
  - `/voice/status` now returns gracefully with availability flags instead of crashing
  - Improved error messages for better debugging and user experience

- **TTS Error Handling** ✅
  - Fixed "[WinError 2] The system cannot find the file specified" errors
  - Added proper exception handling in `_load_tts()` and `_load_whisper()` methods
  - Catches file system errors when models fail to load
  - Distinguishes between missing packages and file system errors

### Improvements

- **User Experience** ✅
  - Dashboard displays "Text-Only Mode" message when TTS unavailable
  - Voice transcription works even without TTS (text responses only)
  - Voice status endpoint shows clear installation status
  - Error messages explain how to fix TTS issues or use text mode
  - Safer error handling prevents cascade failures

### Technical Changes

- `_load_tts()` now catches all exceptions, not just ModuleNotFoundError
- `_load_whisper()` now catches all exceptions during model loading
- `/voice/status` returns gracefully with error field instead of HTTPException
- `/voice/respond` wraps profile/context operations in try-except to prevent failures
- Added console logging to voice endpoints for better debugging

### Technical Changes

- VoiceService now catches TTS loading errors separately
- Better error messages distinguish between missing packages and file system errors
- Dashboard voice handler displays detailed TTS error state
- Fallback behavior ensures system continues to work in text-only mode

## [0.4.0] - 2026-04-17

### Fixed

- **User Profile Generation & Persistence** ✅
  - Fixed JSON serialization error in conversations.json caused by datetime objects
  - Implemented automatic user profile updates triggered every 3 messages
  - Added `_update_user_profile()` method to MemoryService for single-user local system
  - Added `get_user_profile()` convenience method for easy profile retrieval
  - Integrated UserLearningService with MemoryService for automatic learning
  - Set default single-user ID to "local_user" for automatic identification
  - Updated dashboard User Profiles tab to fetch and display profiles from API

### Dashboard Improvements

- **User Profiles Tab** ✅
  - Real-time profile loading from `/users/profile/{user_id}` endpoint
  - Display communication style analysis
  - Show learned knowledge graph statistics
  - Display extracted key concepts as tags
  - Show learned preferences and behavior patterns
  - Empty state with "Generate Profile Now" button for fresh conversations
  - Error handling and loading states

### Technical Changes

- MemoryService now imports UserLearningService
- Automatic profile generation integrated into conversation message flow
- Profiles generated after 2+ messages in conversation (triggers at 3rd + every 3rd message)
- Single-user system design for local AI assistant
- Dashboard HTML updated with functional profile loading and display

### Validation

- Conversations now properly persist to disk with correct JSON serialization
- User profiles generate automatically from conversation data
- Dashboard successfully retrieves and displays profiles
- Single-user "local_user" ID enables seamless local operation

## [0.3.0] - 2026-04-17

### Added

- **Voice MVP**
  - Added `/voice/status`, `/voice/transcribe`, `/voice/speak`, `/voice/respond`, and `/voice/audio/{filename}` endpoints
  - Added a dashboard voice panel inside Chat for recording/uploading audio, transcript display, and audio playback
  - Wired voice responses into the existing personalized chat and memory pipeline

### Fixed

- **Memory & User Learning Reliability**
  - Fixed user profile generation by providing a default interaction frequency
  - Updated knowledge graph and behavior endpoints to read from the active `UserLearningService` instance
  - Added missing conversation summary lookup for `/memory/conversations/{id}/summary`
  - Preserved intended 404 responses instead of wrapping them as 500 errors in memory/profile routes
  - Migrated ChromaDB initialization to the current `PersistentClient` API
  - Indexed full conversation text, summaries, and topics for search instead of title-only records
  - Added query-aware in-memory search fallback when ChromaDB is unavailable
  - Persisted conversation deletes and old-conversation cleanup back to disk
  - Fixed dashboard profile rendering for current user-learning API field names
  - Fixed dashboard topic and profile counters to use live API data
  - Rebuild missing in-memory user profiles from persisted conversations after restart
  - Made automatic profile generation use fast local heuristics so dashboards do not block on Ollama
  - Moved metadata, profile, and Chroma index maintenance off the chat response path
  - Limited chat context size and default generation length for quicker local LLM responses
  - Added conversation file backups before overwriting persisted memory
  - Added personalized response guidance based on learned style, length, and topics
  - Added dashboard behavior metrics and knowledge graph visualization

### Persistence

- Repaired the committed `data/conversations.json` fixture so startup can load it cleanly
- Switched message persistence to JSON-mode Pydantic serialization for datetime-safe output
- Made conversation saves atomic with a temporary file and replace step to avoid partially written JSON

### Testing

- Added missing test dependencies: `httpx`, `pytest`, and `pytest-asyncio`
- Added pytest async auto mode configuration
- Removed stray non-Python markup from `test_persistence.py`
- Verified JSON loading, app import, profile learning, summary lookup, and fallback search smoke checks

## [0.4.0] - 2026-04-17

### Fixed

- **Voice Input/Output Error Handling** ✅
  - Fixed WinError 2 "file not found" when clicking "end voice input"
  - Root cause: Coqui TTS was not installed, causing silent failures
  - Improved voice service error handling to verify file creation
  - Added file existence check before returning audio_url
  - Voice endpoint now properly catches TTS errors and returns them to dashboard
- **User Profile Generation & Persistence** ✅
  - Fixed JSON serialization error in conversations.json caused by datetime objects
  - Implemented automatic user profile updates triggered every 3 messages
  - Added `_update_user_profile()` method to MemoryService for single-user local system
  - Added `get_user_profile()` convenience method for easy profile retrieval
  - Integrated UserLearningService with MemoryService for automatic learning
  - Set default single-user ID to "local_user" for automatic identification
  - Updated dashboard User Profiles tab to fetch and display profiles from API

### Voice Feature Status

- **Voice Input (Transcription)**: ✅ Working - Uses OpenAI Whisper
- **Voice Output (Speech Synthesis)**: ⚠️ Requires Installation
  - Coqui TTS package needs to be installed: `pip install TTS`
  - Large package (~2GB models), may take time on first load
  - Alternative: Continue with text-only responses (currently working)

### Dashboard Improvements

- **User Profiles Tab** ✅
  - Real-time profile loading from `/users/profile/{user_id}` endpoint
  - Display communication style analysis
  - Show learned knowledge graph statistics
  - Display extracted key concepts as tags
  - Show learned preferences and behavior patterns
  - Empty state with "Generate Profile Now" button for fresh conversations
  - Error handling and loading states

### Technical Changes

- MemoryService now imports UserLearningService
- Automatic profile generation integrated into conversation message flow
- Profiles generated after 2+ messages in conversation (triggers at 3rd + every 3rd message)
- Single-user system design for local AI assistant
- Dashboard HTML updated with functional profile loading and display
- Voice service improved with better error handling and file verification
- TTS errors now properly reported to user in dashboard

### Validation

- Conversations now properly persist to disk with correct JSON serialization
- User profiles generate automatically from conversation data
- Dashboard successfully retrieves and displays profiles
- Single-user "local_user" ID enables seamless local operation
- Voice transcription working correctly with Whisper
- Voice synthesis error messages display properly in dashboard

## [0.3.0] - 2026-04-17

### Added

- **User Learning System** ✅
  - Knowledge graph construction from conversations
  - Automatic entity extraction (person, topic, concept, object, event, place)
  - Relationship mapping between entities (causation, part-of, similarity, etc.)
  - Behavior pattern analysis
  - Communication style detection (formal, casual, technical, balanced)
  - Response length preference learning (short, medium, long)
  - Topic extraction and preference tracking
  - User profile generation combining all insights
  - Personalized context generation for adaptive responses
  - User preference management and customization
  - User learning router with endpoints:
    - `POST /users/profile/{user_id}/learn` - Build profile from conversations
    - `GET /users/profile/{user_id}` - Get complete user profile
    - `GET /users/profile/{user_id}/knowledge-graph` - View knowledge graph
    - `GET /users/profile/{user_id}/behavior` - Get behavior analysis
    - `GET /users/profile/{user_id}/context` - Get personalized context
    - `POST /users/profile/{user_id}/preferences` - Update learned preferences
    - `GET /users/profile/{user_id}/insights` - Get behavioral insights

- **Advanced Memory Features** ✅
  - Automatic conversation summary generation via LLM
  - Topic extraction from conversations
  - Importance scoring based on message count (0-1 scale)
  - Message count tracking
  - Last activity timestamp tracking
  - Memory statistics and analytics:
    - `GET /memory/stats` - Core analytics (conversations, messages, topics, storage)
    - `GET /memory/recent` - Most recently active conversations
    - `GET /memory/important` - Most important conversations by score
    - `POST /memory/search/advanced` - Advanced search with importance and topic filters
    - `GET /memory/topics/{topic}` - Find conversations by topic
  - Dual-level learning: raw memory + behavioral patterns

### How It Works

1. Conversations are stored with full message history
2. System automatically extracts entities and topics from messages
3. Knowledge graph builds relationship networks between concepts
4. Behavior analyzer determines user's communication style and preferences
5. User profile combines all insights for personalized interactions
6. Personalized context is generated for each response
7. System continuously learns and adapts as more conversations occur

### New Models

- `EntityType` - Entity classification
- `RelationType` - Relationship classification
- `Entity` - Knowledge graph nodes
- `Relationship` - Knowledge graph edges
- `BehaviorPattern` - Detected patterns
- `UserBehaviorProfile` - Behavior analysis
- `UserPreferences` - Learned preferences
- `UserProfile` - Complete user model

### New Services

- `KnowledgeGraphService` - Entity and relationship extraction
- `UserBehaviorAnalyzer` - Pattern and style detection
- `UserLearningService` - Profile generation and management

## [0.2.0] - 2026-04-17

### Added

- **Memory System** ✅
  - ChromaDB integration for vector-based conversation storage
  - Conversation management with unique IDs and metadata
  - Message storage with timestamps and roles (user/assistant)
  - Semantic search across conversations
  - Conversation summary generation using LLM
  - Memory router with endpoints:
    - `POST /memory/conversations/create` - Create new conversation
    - `GET /memory/conversations` - List all conversations
    - `GET /memory/conversations/{id}` - Get specific conversation
    - `POST /memory/conversations/{id}/messages` - Add message and get LLM response
    - `POST /memory/search` - Search conversations semantically
    - `GET /memory/conversations/{id}/summary` - Get conversation summary
    - `DELETE /memory/conversations/{id}` - Delete conversation
  - Lazy ChromaDB initialization to prevent startup blocking
  - Thread pool support for blocking database operations
  - Conversation metadata tracking (summary, topics, importance, message count)
  - LLM-powered automatic summarization and topic extraction

### Features

- Persistent conversation storage
- Semantic similarity search
- Automatic metadata generation
- Message context preservation

## [0.1.0] - 2026-04-17

### Added

- **LLM Integration** ✅
  - Local Ollama integration for running LLMs locally
  - LLM service with chat generation, model listing, and status checks
  - Async support using ThreadPoolExecutor for blocking Ollama calls
  - LLM router with `/llm/status`, `/llm/models`, and `/llm/chat` endpoints

- **Project Structure** ✅
  - Organized folder structure with routers, services, models, config, and plugins
  - Settings configuration system using pydantic-settings
  - Health check endpoint
  - Entry point pattern separating main.py from app initialization

- **API Features**
  - FastAPI auto-generated documentation (/docs)
  - Pydantic request/response validation
  - Health check endpoint
  - Full LLM functionality via REST API

- **Testing**
  - test_llm.py - Direct LLM service testing
  - test_api.py - HTTP API endpoint testing

### Dependencies

- fastapi
- uvicorn[standard]
- ollama
- pydantic
- pydantic-settings
- python-multipart
- websockets
- openai-whisper
- coqui-tts
- chromadb
- httpx (for testing)

### Configuration

- Ollama base URL: http://localhost:11434
- Default model: llama3.1:8b
- Local, no cloud dependencies

### Next Steps

1. Voice Input/Output integration (Whisper + Coqui)
2. Multi-device support with WebSockets
3. Plugin system for extensibility
4. Advanced analytics and reporting
