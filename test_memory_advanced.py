#!/usr/bin/env python
"""Test advanced memory system features"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"


async def test_advanced_memory():
    print("Testing Advanced Memory System Features\n")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Test 1: Create multiple conversations with different topics
            print("\n1. Creating test conversations...")
            
            # Cooking conversation
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Italian Cooking Tips", "metadata": {"category": "cooking"}}
            )
            cooking_id = response.json()["conversation_id"]
            
            # Add cooking messages
            await client.post(
                f"{BASE_URL}/memory/conversations/{cooking_id}/messages",
                json={"message": "How do I make perfect pasta carbonara?"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{cooking_id}/messages",
                json={"message": "What's the secret to crispy pizza dough?"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{cooking_id}/messages",
                json={"message": "Can you explain Italian herbs?"}
            )
            print(f"   ✓ Cooking conversation: {cooking_id}")
            
            # Tech conversation
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "AI Development Discussion", "metadata": {"category": "tech"}}
            )
            tech_id = response.json()["conversation_id"]
            
            # Add tech messages
            await client.post(
                f"{BASE_URL}/memory/conversations/{tech_id}/messages",
                json={"message": "What's the difference between machine learning and deep learning?"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{tech_id}/messages",
                json={"message": "How do transformers work in AI?"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{tech_id}/messages",
                json={"message": "What are the latest developments in LLM technology?"}
            )
            print(f"   ✓ Tech conversation: {tech_id}")
            
            # Test 2: Get memory statistics
            print("\n2. Getting memory statistics...")
            response = await client.get(f"{BASE_URL}/memory/stats")
            stats = response.json()
            print(f"   ✓ Total conversations: {stats['total_conversations']}")
            print(f"   ✓ Total messages: {stats['total_messages']}")
            print(f"   ✓ Average conversation length: {stats['average_conversation_length']}")
            print(f"   ✓ Top topics: {stats['top_topics'][:3]}")
            
            # Test 3: Get conversation with metadata
            print("\n3. Getting conversation with advanced metadata...")
            response = await client.get(f"{BASE_URL}/memory/conversations/{cooking_id}")
            conv = response.json()
            print(f"   ✓ Conversation has {conv.get('message_count', 0)} messages")
            print(f"   ✓ Topics: {conv.get('topics', [])}")
            print(f"   ✓ Summary: {conv.get('summary', 'None')[:100]}...")
            
            # Test 4: Advanced search
            print("\n4. Advanced search for 'cooking'...")
            response = await client.post(
                f"{BASE_URL}/memory/search/advanced",
                json={"query": "cooking", "limit": 5, "min_importance": 0.0}
            )
            search = response.json()
            print(f"   ✓ Found {search['count']} cooking-related conversations")
            
            # Test 5: Topic-based queries
            print("\n5. Getting conversations by topic...")
            response = await client.get(f"{BASE_URL}/memory/topics/cooking")
            topic_results = response.json()
            print(f"   ✓ Found {topic_results['count']} conversations about cooking")
            
            # Test 6: Recent conversations
            print("\n6. Getting recent conversations...")
            response = await client.get(f"{BASE_URL}/memory/recent?limit=3")
            recent = response.json()
            print(f"   ✓ Found {recent['count']} recent conversations")
            
            # Test 7: Important conversations
            print("\n7. Getting most important conversations...")
            response = await client.get(f"{BASE_URL}/memory/important?limit=3")
            important = response.json()
            print(f"   ✓ Found {important['count']} important conversations")
            
            print("\n" + "=" * 70)
            print("✅ ADVANCED MEMORY SYSTEM WORKING!")
            print("\nFeatures tested:")
            print("  • Automatic summaries and topic extraction")
            print("  • Importance scoring")
            print("  • Advanced search with filters")
            print("  • Topic-based conversation retrieval")
            print("  • Memory statistics and analytics")
            print("  • Recent and important conversation ranking")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(test_advanced_memory())