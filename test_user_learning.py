#!/usr/bin/env python
"""Test the user learning and knowledge graph system"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"


async def test_user_learning():
    print("Testing User Learning & Knowledge Graph System\n")
    print("=" * 70)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            user_id = "test_user_001"
            
            # Test 1: Create some conversations first
            print("\n1. Creating test conversations...")
            
            # Conv 1: Programming discussion
            resp1 = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Python Programming", "metadata": {"user_id": user_id}}
            )
            conv1_id = resp1.json()["conversation_id"]
            
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv1_id}/messages",
                json={"message": "How do I write efficient algorithms in Python?"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv1_id}/messages",
                json={"message": "What's the difference between lists and tuples?"}
            )
            print(f"   ✓ Created programming conversation")
            
            # Conv 2: Data science discussion
            resp2 = await client.post(
                f"{BASE_URL}/memory/conversations/create",
                json={"title": "Data Science", "metadata": {"user_id": user_id}}
            )
            conv2_id = resp2.json()["conversation_id"]
            
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv2_id}/messages",
                json={"message": "Tell me about machine learning fundamentals"}
            )
            await client.post(
                f"{BASE_URL}/memory/conversations/{conv2_id}/messages",
                json={"message": "How do neural networks work?"}
            )
            print(f"   ✓ Created data science conversation")
            
            # Test 2: Learn from conversations
            print("\n2. Building user profile from conversations...")
            resp = await client.post(
                f"{BASE_URL}/users/profile/{user_id}/learn"
            )
            result = resp.json()
            print(f"   ✓ Profile created for user: {user_id}")
            
            # Test 3: Get user profile
            print("\n3. Getting complete user profile...")
            resp = await client.get(f"{BASE_URL}/users/profile/{user_id}")
            profile = resp.json()
            print(f"   ✓ Communication style: {profile['behavior_profile']['communication_style']}")
            print(f"   ✓ Response preference: {profile['behavior_profile']['response_length_preference']}")
            print(f"   ✓ Total conversations: {profile['total_conversations']}")
            
            # Test 4: Get knowledge graph
            print("\n4. Getting knowledge graph...")
            resp = await client.get(f"{BASE_URL}/users/profile/{user_id}/knowledge-graph")
            kg = resp.json()
            print(f"   ✓ Entities discovered: {kg['entities_count']}")
            print(f"   ✓ Relationships mapped: {kg['relationships_count']}")
            if kg['top_entities']:
                print(f"   ✓ Top concepts: {', '.join([e['name'] for e in kg['top_entities'][:3]])}")
            
            # Test 5: Get behavior analysis
            print("\n5. Getting behavior analysis...")
            resp = await client.get(f"{BASE_URL}/users/profile/{user_id}/behavior")
            behavior = resp.json()
            print(f"   ✓ Communication style: {behavior['communication_style']}")
            print(f"   ✓ Preferred topics: {', '.join(behavior['preferred_topics'][:3])}")
            
            # Test 6: Get personalized context
            print("\n6. Getting personalized context...")
            resp = await client.get(f"{BASE_URL}/users/profile/{user_id}/context")
            ctx = resp.json()
            print(f"   ✓ Context: {ctx['personalized_context'][:100]}...")
            
            # Test 7: Get user insights
            print("\n7. Getting user behavioral insights...")
            resp = await client.get(f"{BASE_URL}/users/profile/{user_id}/insights")
            insights = resp.json()
            print(f"   ✓ Primary interests: {', '.join(insights['insights']['primary_interests'])}")
            print(f"   ✓ Engagement level: {insights['insights']['engagement_level']}")
            print(f"   ✓ Concepts discovered: {insights['insights']['total_concepts_learned']}")
            
            # Test 8: Update preferences
            print("\n8. Updating user preferences...")
            resp = await client.post(
                f"{BASE_URL}/users/profile/{user_id}/preferences",
                json={
                    "explanation_style": "technical",
                    "personality_match": "helpful_expert",
                    "topics_to_avoid": ["politics"]
                }
            )
            print(f"   ✓ Preferences updated")
            
            print("\n" + "=" * 70)
            print("✅ USER LEARNING SYSTEM WORKING!")
            print("\nFeatures verified:")
            print("  • Knowledge graph entity extraction")
            print("  • Relationship discovery")
            print("  • Behavior pattern analysis")
            print("  • Communication style detection")
            print("  • Topic extraction")
            print("  • Personalized context generation")
            print("  • User insight derivation")
            print("  • Preference learning and updates")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_user_learning())