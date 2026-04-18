# NexusAI Changelog

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
