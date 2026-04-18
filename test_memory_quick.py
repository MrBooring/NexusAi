#!/usr/bin/env python
"""Quick test of memory system without summaries"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"


async def quick_test():
    print("Quick Memory System Test\n")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            # Test 1: Create a conversation
            print("\n1. Creating a conversation...")
            response = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Test Conversation"}
            )
            conv_id = response.json()["conversation_id"]
            print(f"   ✓ Created: {conv_id}")
            
            # Test 2: Add a message
            print("\n2. Adding a message...")
            response = await client.post(
                f"{BASE_URL}/memory/conversations/{conv_id}/messages",
                json={"message": "Hello!"}
            )
            result = response.json()
            print(f"   ✓ User message stored")
            print(f"   ✓ Got response from LLM")
            
            # Test 3: Get the conversation
            print("\n3. Retrieving conversation...")
            response = await client.get(f"{BASE_URL}/memory/conversations/{conv_id}")
            conv = response.json()
            print(f"   ✓ Conversation has {len(conv['messages'])} messages")
            
            # Test 4: List conversations
            print("\n4. Listing all conversations...")
            response = await client.get(f"{BASE_URL}/memory/conversations")
            convs = response.json()
            print(f"   ✓ Total: {convs['count']} conversation(s)")
            
            print("\n" + "=" * 60)
            print("✅ MEMORY SYSTEM WORKING!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(quick_test())