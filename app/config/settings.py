from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    app_name: str = "NexusAI"
    version: str = "0.1.0"
    debug: bool = True

    # LLM settings
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.1:8b"

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