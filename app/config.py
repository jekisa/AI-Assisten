import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Konfigurasi aplikasi Asisten AI Dea Trans Group.
    Mendukung pembacaan otomatis dari environment variables atau file .env.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # App Settings
    APP_NAME: str = "Dea Trans Group AI Assistant"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_DEBUG: bool = True

    # LLM Settings (OpenAI / OpenAI-Compatible)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # Web Search Tool Settings
    TAVILY_API_KEY: Optional[str] = None

    # Vector DB (ChromaDB) Settings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "deatrans_knowledge"
    
    # Ambang batas jarak (distance). Jika distance terdekat > threshold,
    # dokumen dianggap tidak memadai (tidak relevan), sehingga beralih ke Fallback Web Search.
    RETRIEVAL_DISTANCE_THRESHOLD: float = 1.38
    RETRIEVAL_TOP_K: int = 3


settings = Settings()
