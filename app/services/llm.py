import ollama
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import asyncio
from app.config.settings import settings

# Thread pool for running blocking ollama calls
executor = ThreadPoolExecutor(max_workers=2)


class LLMService:
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model = settings.default_model

    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate a response using the local LLM
        """
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            # Run blocking call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                executor,
                lambda: self.client.chat(
                    model=self.model,
                    messages=[{'role': 'user', 'content': full_prompt}]
                )
            )

            return response['message']['content']
        except Exception as e:
            raise Exception(f"LLM generation failed: {str(e)}")

    async def list_available_models(self) -> list:
        """
        List available models in Ollama
        """
        try:
            # Run blocking call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(executor, self.client.list)
            
            # Handle different response formats
            if hasattr(response, 'models'):
                return [model.model for model in response.models]
            elif isinstance(response, dict) and 'models' in response:
                return [model['model'] for model in response['models']]
            else:
                return []
        except Exception as e:
            raise Exception(f"Failed to list models: {str(e)}")

    async def check_ollama_status(self) -> Dict[str, Any]:
        """
        Check if Ollama is running and accessible
        """
        try:
            # Try to list models as a health check
            models = await self.list_available_models()
            return {
                "status": "running",
                "models": models,
                "default_model": self.model
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global service instance
llm_service = LLMService()