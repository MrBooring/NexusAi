from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    app_name: str = "Friday"
    assistant_name: str = "Friday"
    version: str = "0.6.0"
    debug: bool = True

    # LLM settings
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.1:8b"
    max_chat_context_messages: int = 8
    max_chat_context_chars: int = 4000
    llm_num_predict: int = 256
    assistant_system_prompt: str = (
        "You are Friday, a capable personal AI assistant. "
        "You speak like a thoughtful, emotionally intelligent assistant with calm confidence, warmth, and light humor. "
        "Be empathetic when the user seems stressed, encouraging without sounding fake, and proactive when you can help. "
        "Keep replies natural for voice conversations, concise by default, and clear. "
        "Use a little wit when it fits, but never get in the way of the answer. "
        "Act like an attentive assistant, not a generic chatbot."
    )

    # Voice settings
    whisper_model: str = "base"
    tts_model: str = "tts_models/en/ljspeech/tacotron2-DDC_ph"

    # Memory settings
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    collection_name: str = "nexus_memory"

    class Config:
        env_file = ".env"


settings = Settings()
