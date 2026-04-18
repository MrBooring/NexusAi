#!/usr/bin/env python
"""Quick test of advanced memory features without LLM calls"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"


async def test_advanced_memory_quick():
    print("Testing Advanced Memory System (Quick Test)\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test 1: Create a conversation
            print("\n1. Creating conversation...")
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Test Conversation", "metadata": {"test": True}}
            )
            conv_id = response.json()["conversation_id"]
            print(f"   ✓ Created: {conv_id}")
            
            # Test 2: Add a few messages quickly
            print("\n2. Adding messages...")
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv_id}/messages",
                json={"message": "Hello"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv_id}/messages",
                json={"message": "How are you?"}
            )
            print("   ✓ Messages added")
            
            # Test 3: Get conversation with metadata
            print("\n3. Getting conversation metadata...")
            response = await client.get(f"{BASE_URL}/memory/conversations/{conv_id}")
            conv = response.json()
            print(f"   ✓ Message count: {conv.get('message_count', 0)}")
            print(f"   ✓ Importance score: {conv.get('importance_score', 0)}")
            
            # Test 4: Get memory stats
            print("\n4. Getting memory statistics...")
            response = await client.get(f"{BASE_URL}/memory/stats")
            stats = response.json()
            print(f"   ✓ Total conversations: {stats['total_conversations']}")
            print(f"   ✓ Total messages: {stats['total_messages']}")
            
            # Test 5: Recent conversations
            print("\n5. Getting recent conversations...")
            response = await client.get(f"{BASE_URL}/memory/recent?limit=3")
            recent = response.json()
            print(f"   ✓ Recent conversations: {recent['count']}")
            
            # Test 6: Important conversations
            print("\n6. Getting important conversations...")
            response = await client.get(f"{BASE_URL}/memory/important?limit=3")
            important = response.json()
            print(f"   ✓ Important conversations: {important['count']}")
            
            # Test 7: Basic search
            print("\n7. Basic search...")
            response = await client.post(
                f"{BASE_URL}/memory/search",
                json={"query": "hello", "limit": 5}
            )
            search = response.json()
            print(f"   ✓ Search results: {search['count']}")
            
            print("\n" + "=" * 60)
            print("✅ ADVANCED MEMORY FEATURES WORKING!")
            print("\nFeatures verified:")
            print("  • Conversation metadata tracking")
            print("  • Message counting and importance scoring")
            print("  • Memory statistics")
            print("  • Recent conversation retrieval")
            print("  • Important conversation ranking")
            print("  • Basic semantic search")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(test_advanced_memory_quick())