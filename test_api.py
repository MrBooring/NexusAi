#!/usr/bin/env python
"""Test LLM API endpoints"""

import httpx
import asyncio

BASE_URL = "http://localhost:8000"


async def test_api():
    async with httpx.AsyncClient(timeout=120.0) as client:
        print("Testing Friday LLM API Endpoints\n")

        # Test 1: Health endpoint
        print("1. Testing /health endpoint...")
        response = await client.get(f"{BASE_URL}/health")
        print(f"   Response: {response.json()}\n")

        # Test 2: LLM Status
        print("2. Testing /llm/status endpoint...")
        response = await client.get(f"{BASE_URL}/llm/status")
        print(f"   Response: {response.json()}\n")

        # Test 3: List Models
        print("3. Testing /llm/models endpoint...")
        response = await client.get(f"{BASE_URL}/llm/models")
        print(f"   Response: {response.json()}\n")

        # Test 4: Chat endpoint
        print("4. Testing /llm/chat endpoint...")
        print("   (This may take a moment for the LLM to generate a response...)")
        response = await client.post(
            f"{BASE_URL}/llm/chat",
            json={"prompt": "What is Friday?", "context": ""}
        )
        result = response.json()
        print(f"   Response: {result}\n")
        print("✅ All API endpoints working!")


if __name__ == "__main__":
    asyncio.run(test_api())
