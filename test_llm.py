#!/usr/bin/env python
"""Test script for LLM integration"""

import asyncio
from app.services.llm import llm_service


async def test_llm():
    print("Testing LLM Integration...\n")

    # Test 1: Check Ollama status
    print("1. Checking Ollama Status...")
    status = await llm_service.check_ollama_status()
    print(f"   Status: {status}\n")

    if status['status'] != 'running':
        print("❌ Ollama is not running!")
        return

    # Test 2: List available models
    print("2. Available Models:")
    models = await llm_service.list_available_models()
    for model in models:
        print(f"   - {model}")
    print()

    # Test 3: Generate a simple response
    print("3. Testing Chat Generation...")
    try:
        response = await llm_service.generate_response(
            prompt="Hello! What is 2 + 2?",
            context=""
        )
        print(f"   Response: {response}\n")
        print("✅ LLM Integration is working!")
    except Exception as e:
        print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(test_llm())