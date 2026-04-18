import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import uuid
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from app.config.settings import settings
from app.models.conversation import Conversation, Message
from app.services.llm import llm_service
from app.services.user_learning import user_learning_service

# Thread pool for ChromaDB operations
executor = ThreadPoolExecutor(max_workers=2)

# Default user ID for single-user local system
DEFAULT_USER_ID = "local_user"


class MemoryService:
    def __init__(self):
        # Initialize ChromaDB client in a lazy manner
        self._client = None
        self._collection = None
        
        # In-memory storage for conversation data
        self.conversations: Dict[str, Conversation] = {}
        
        # Persistent storage
        self.data_dir = "./data"
        self.conversations_file = os.path.join(self.data_dir, "conversations.json")
        
        # Load existing conversations on startup
        self._load_conversations_from_disk()

    def _ensure_initialized(self):
        """Ensure ChromaDB is initialized"""
        if self._client is None:
            try:
                # Initialize ChromaDB client
                self._client = chromadb.Client(
                    ChromaSettings(
                        chroma_db_impl="duckdb",
                        persist_directory="./data/chroma",
                        anonymized_telemetry=False
                    )
                )
                
                # Get or create collection for conversations
                self._collection = self._client.get_or_create_collection(
                    name=settings.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Warning: ChromaDB initialization failed: {e}")
                self._collection = None

    def _load_conversations_from_disk(self):
        """Load conversations from persistent storage"""
        try:
            if os.path.exists(self.conversations_file):
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for conv_data in data.get('conversations', []):
                        # Convert dict back to Conversation object
                        messages = [Message(**msg) for msg in conv_data['messages']]
                        conversation = Conversation(
                            conversation_id=conv_data['conversation_id'],
                            title=conv_data.get('title'),
                            messages=messages,
                            created_at=datetime.fromisoformat(conv_data['created_at']),
                            updated_at=datetime.fromisoformat(conv_data['updated_at']),
                            metadata=conv_data.get('metadata', {}),
                            summary=conv_data.get('summary'),
                            topics=conv_data.get('topics', []),
                            importance_score=conv_data.get('importance_score', 1.0),
                            message_count=conv_data.get('message_count', 0),
                            last_activity=datetime.fromisoformat(conv_data['last_activity'])
                        )
                        self.conversations[conversation.conversation_id] = conversation
                print(f"Loaded {len(self.conversations)} conversations from disk")
        except Exception as e:
            print(f"Warning: Failed to load conversations from disk: {e}")

    def _save_conversations_to_disk(self):
        """Save conversations to persistent storage"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            data = {
                'conversations': [
                    {
                        'conversation_id': conv.conversation_id,
                        'title': conv.title,
                        'messages': [msg.dict() for msg in conv.messages],
                        'created_at': conv.created_at.isoformat(),
                        'updated_at': conv.updated_at.isoformat(),
                        'metadata': conv.metadata,
                        'summary': conv.summary,
                        'topics': conv.topics,
                        'importance_score': conv.importance_score,
                        'message_count': conv.message_count,
                        'last_activity': conv.last_activity.isoformat()
                    }
                    for conv in self.conversations.values()
                ]
            }
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save conversations to disk: {e}")

    def _ensure_initialized(self):
        """Ensure ChromaDB is initialized"""
        if self._client is None:
            try:
                # Initialize ChromaDB client
                self._client = chromadb.Client(
                    ChromaSettings(
                        chroma_db_impl="duckdb",
                        persist_directory="./data/chroma",
                        anonymized_telemetry=False
                    )
                )
                
                # Get or create collection for conversations
                self._collection = self._client.get_or_create_collection(
                    name=settings.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Warning: ChromaDB initialization failed: {e}")
                self._collection = None

    @property
    def collection(self):
        """Lazy initialization of collection"""
        self._ensure_initialized()
        return self._collection

    async def create_conversation(self, title: Optional[str] = None, metadata: Optional[dict] = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        
        conversation = Conversation(
            conversation_id=conversation_id,
            title=title or f"Conversation {conversation_id[:8]}",
            messages=[],
            metadata=metadata or {}
        )
        
        self.conversations[conversation_id] = conversation
        
        # Save to disk
        self._save_conversations_to_disk()
        
        # Store in ChromaDB for vector search if available
        if self.collection is not None:
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    executor,
                    lambda: self.collection.add(
                        ids=[conversation_id],
                        metadatas=[{
                            "title": conversation.title,
                            "created_at": conversation.created_at.isoformat(),
                            "conversation_id": conversation_id
                        }],
                        documents=[conversation.title]
                    )
                )
            except Exception as e:
                print(f"Warning: Failed to add conversation to ChromaDB: {e}")
        
        return conversation_id

    async def add_message(self, conversation_id: str, role: str, content: str) -> Conversation:
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        message = Message(role=role, content=content)
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        conversation.last_activity = datetime.now()
        conversation.message_count = len(conversation.messages)
        
        # Auto-generate summary and topics for longer conversations
        # For testing: generate after 2 messages, then every 2 messages
        if conversation.message_count >= 2 and conversation.message_count % 2 == 0:
            await self._update_conversation_metadata(conversation)
        
        # Update importance score based on conversation length and recency
        conversation.importance_score = min(1.0, conversation.message_count / 20.0)
        
        # Auto-update user profile for single-user system
        if conversation.message_count >= 2 and conversation.message_count % 3 == 0:
            await self._update_user_profile()
        
        # Save to disk after every message
        self._save_conversations_to_disk()
        
        return conversation

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)

    async def get_all_conversations(self) -> List[Conversation]:
        """Get all conversations"""
        return list(self.conversations.values())

    async def search_conversations(self, query: str, limit: int = 5) -> List[Conversation]:
        """Search conversations using semantic similarity"""
        if self.collection is None:
            # Fallback to in-memory search
            return list(self.conversations.values())[:limit]
        
        try:
            # Query ChromaDB for similar documents
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                executor,
                lambda: self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
            )
            
            if not results['ids'] or not results['ids'][0]:
                return []
            
            # Return matching conversations
            conversation_ids = results['ids'][0]
            return [self.conversations[cid] for cid in conversation_ids if cid in self.conversations]
        except Exception as e:
            print(f"Search error: {e}")
            return list(self.conversations.values())[:limit]

    async def _update_conversation_metadata(self, conversation: Conversation):
        """Update summary and topics for a conversation"""
        try:
            print(f"Generating metadata for conversation {conversation.conversation_id[:8]}... ({conversation.message_count} messages)")
            
            # Generate summary
            conversation_text = "\n".join([
                f"{msg.role.upper()}: {msg.content}"
                for msg in conversation.messages
            ])
            
            summary_prompt = f"""Please provide a concise 2-3 sentence summary of this conversation:

{conversation_text}

Summary:"""
            
            summary = await llm_service.generate_response(
                prompt=summary_prompt,
                context="You are a helpful assistant that creates concise, informative summaries."
            )
            conversation.summary = summary
            print(f"Generated summary: {summary[:100]}...")
            
            # Extract topics
            topics_prompt = f"""Extract 3-5 key topics or themes from this conversation. Return only a comma-separated list of topics:

{conversation_text}

Topics:"""
            
            topics_response = await llm_service.generate_response(
                prompt=topics_prompt,
                context="You are a helpful assistant that extracts key topics from conversations."
            )
            
            # Parse topics from response
            topics = [topic.strip() for topic in topics_response.split(',') if topic.strip()]
            conversation.topics = topics[:5]  # Limit to 5 topics
            print(f"Generated topics: {conversation.topics}")
            
        except Exception as e:
            print(f"Warning: Failed to update conversation metadata: {e}")

    async def _update_user_profile(self):
        """Automatically update user profile for single-user system"""
        try:
            print(f"Updating user profile for {DEFAULT_USER_ID}...")
            
            # Get all conversations
            conversations = list(self.conversations.values())
            if not conversations:
                return
            
            # Collect all messages
            all_messages = []
            for conv in conversations:
                for msg in conv.messages:
                    all_messages.append((msg.role, msg.content))
            
            # Update user profile
            profile = await user_learning_service.learn_from_conversation(
                user_id=DEFAULT_USER_ID,
                messages=all_messages,
                conversation_count=len(conversations)
            )
            
            print(f"User profile updated: {len(profile.entities)} entities, {len(profile.relationships)} relationships")
            
        except Exception as e:
            print(f"Warning: Failed to update user profile: {e}")

    async def get_user_profile(self, user_id: str = DEFAULT_USER_ID):
        """Get user profile for single-user system"""
        return await user_learning_service.get_user_profile(user_id)

    async def get_memory_stats(self) -> dict:
        """Get comprehensive memory statistics"""
        conversations = list(self.conversations.values())
        
        if not conversations:
            return {
                "total_conversations": 0,
                "total_messages": 0,
                "average_conversation_length": 0.0,
                "oldest_conversation": None,
                "newest_conversation": None,
                "top_topics": [],
                "storage_size_mb": 0.0
            }
        
        total_messages = sum(len(conv.messages) for conv in conversations)
        avg_length = total_messages / len(conversations) if conversations else 0
        
        # Find oldest and newest
        oldest = min(conv.created_at for conv in conversations)
        newest = max(conv.created_at for conv in conversations)
        
        # Count topics
        topic_counts = {}
        for conv in conversations:
            for topic in conv.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        top_topics = sorted(
            [{"topic": topic, "count": count} for topic, count in topic_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )[:10]  # Top 10 topics
        
        # Estimate storage size (rough calculation)
        storage_mb = (total_messages * 0.001) + (len(conversations) * 0.01)  # Rough estimate
        
        return {
            "total_conversations": len(conversations),
            "total_messages": total_messages,
            "average_conversation_length": round(avg_length, 2),
            "oldest_conversation": oldest,
            "newest_conversation": newest,
            "top_topics": top_topics,
            "storage_size_mb": round(storage_mb, 2)
        }

    async def search_conversations_advanced(self, query: str, limit: int = 5, 
                                          min_importance: float = 0.0, 
                                          topics: Optional[List[str]] = None) -> List[Conversation]:
        """Advanced search with filters"""
        # Get basic semantic search results
        candidates = await self.search_conversations(query, limit * 2)  # Get more candidates
        
        # Apply filters
        filtered = []
        for conv in candidates:
            # Importance filter
            if conv.importance_score < min_importance:
                continue
                
            # Topics filter
            if topics and not any(topic in conv.topics for topic in topics):
                continue
                
            filtered.append(conv)
        
        return filtered[:limit]

    async def get_conversations_by_topic(self, topic: str, limit: int = 10) -> List[Conversation]:
        """Get conversations that contain a specific topic"""
        matching = [
            conv for conv in self.conversations.values()
            if topic.lower() in [t.lower() for t in conv.topics]
        ]
        
        # Sort by importance and recency
        matching.sort(key=lambda x: (x.importance_score, x.last_activity), reverse=True)
        return matching[:limit]

    async def get_recent_conversations(self, limit: int = 5) -> List[Conversation]:
        """Get most recently active conversations"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda x: x.last_activity, reverse=True)
        return conversations[:limit]

    async def get_important_conversations(self, limit: int = 5) -> List[Conversation]:
        """Get most important conversations by score"""
        conversations = list(self.conversations.values())
        conversations.sort(key=lambda x: x.importance_score, reverse=True)
        return conversations[:limit]

    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

    async def delete_old_conversations(self, days: int = 30) -> int:
        """Delete conversations older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        to_delete = [
            cid for cid, conv in self.conversations.items()
            if conv.created_at < cutoff_date
        ]
        
        for cid in to_delete:
            del self.conversations[cid]
        
        return len(to_delete)


# Global memory service instance
memory_service = MemoryService()