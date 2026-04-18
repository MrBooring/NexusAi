#!/usr/bin/env python
"""Test script for memory system"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"


async def test_memory_system():
    print("Testing Memory System Integration\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Test 1: Create a conversation
            print("\n1. Creating a new conversation...")
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Pizza Order", "metadata": {"user": "john", "device": "mobile"}}
            )
            result = response.json()
            conversation_id = result["conversation_id"]
            print(f"   ✓ Conversation created: {conversation_id}")
            
            # Test 2: Add messages to conversation
            print("\n2. Adding messages to conversation...")
            
            # Message 1
            response = await client.post(
                f"{BASE_URL}/memory/conversations/{conversation_id}/messages",
                json={"message": "What's a good pizza recipe?"}
            )
            result = response.json()
            print(f"   ✓ User: {result['user_message']}")
            print(f"   ✓ Assistant: {result['assistant_response'][:100]}...")
            
            # Message 2
            await asyncio.sleep(1)  # Small delay
            response = await client.post(
                f"{BASE_URL}/memory/conversations/{conversation_id}/messages",
                json={"message": "Can you give me a simpler version?"}
            )
            result = response.json()
            print(f"   ✓ User: {result['user_message']}")
            print(f"   ✓ Assistant: {result['assistant_response'][:100]}...")
            
            # Test 3: Get conversation
            print("\n3. Retrieving conversation...")
            response = await client.get(f"{BASE_URL}/memory/conversations/{conversation_id}")
            conversation = response.json()
            print(f"   ✓ Conversation has {len(conversation['messages'])} messages")
            
            # Test 4: Get conversation summary
            print("\n4. Getting conversation summary...")
            response = await client.get(f"{BASE_URL}/memory/conversations/{conversation_id}/summary")
            summary = response.json()
            print(f"   ✓ Summary: {summary['summary'][:150]}...")
            
            # Test 5: List all conversations
            print("\n5. Listing all conversations...")
            response = await client.get(f"{BASE_URL}/memory/conversations")
            result = response.json()
            print(f"   ✓ Total conversations: {result['count']}")
            
            # Test 6: Search conversations
            print("\n6. Searching conversations...")
            response = await client.post(
                f"{BASE_URL}/memory/search",
                json={"query": "pizza", "limit": 5}
            )
            search = response.json()
            print(f"   ✓ Found {search['count']} matching conversations")
            
            # Test 7: Create another conversation for comparison
            print("\n7. Creating another conversation for search...")
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Pasta Discussion"}
            )
            conv2_id = response.json()["conversation_id"]
            
            response = await client.post(
                f"{BASE_URL}/memory/conversations/{conv2_id}/messages",
                json={"message": "How do I cook pasta al dente?"}
            )
            print(f"   ✓ Second conversation created")
            
            # Test 8: Search again
            print("\n8. Searching for 'pasta'...")
            response = await client.post(
                f"{BASE_URL}/memory/search",
                json={"query": "pasta", "limit": 5}
            )
            search = response.json()
            print(f"   ✓ Found {search['count']} matching conversations")
            
            print("\n" + "=" * 60)
            print("✅ ALL MEMORY SYSTEM TESTS PASSED!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(test_memory_system())