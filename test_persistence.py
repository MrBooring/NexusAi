import asyncio
from app.services.memory import memory_service

async def test_persistence():
    print("=== Testing Friday Persistence & Learning ===\n")

    # Create a conversation
    print("1. Creating conversation...")
    conv_id = await memory_service.create_conversation(title="Test Conversation")
    print(f"   Created: {conv_id[:8]}...")

    # Add some messages
    print("\n2. Adding messages...")
    await memory_service.add_message(conv_id, "user", "Hello, I'm testing the AI system.")
    print("   Added user message")

    await memory_service.add_message(conv_id, "assistant", "Hello! I'm happy to help you test the system. What would you like to know?")
    print("   Added assistant message")

    await memory_service.add_message(conv_id, "user", "Can you tell me about machine learning and AI?")
    print("   Added user message (should trigger summary)")

    await memory_service.add_message(conv_id, "assistant", "Machine learning is a subset of AI that focuses on algorithms that can learn from data. AI encompasses broader concepts including reasoning, problem-solving, and perception.")
    print("   Added assistant message")

    # Check the conversation
    print("\n3. Checking conversation...")
    conv = await memory_service.get_conversation(conv_id)
    print(f"   Messages: {conv.message_count}")
    print(f"   Summary: {conv.summary or 'None'}")
    print(f"   Topics: {conv.topics}")

    # Check persistence
    print("\n4. Testing persistence...")
    print(f"   Conversations in memory: {len(memory_service.conversations)}")

    # Force save
    memory_service._save_conversations_to_disk()
    print("   Saved to disk")

    print("\n=== Test Complete ===")
    print("Restart the server and run this script again to verify persistence!")

if __name__ == "__main__":
    asyncio.run(test_persistence())
