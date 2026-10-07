from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "VoiceOS"
    environment: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # LLM Providers
    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # LiveKit Voice Stack
    livekit_url: Optional[str] = Field(default=None, alias="LIVEKIT_URL")
    livekit_api_key: Optional[str] = Field(default=None, alias="LIVEKIT_API_KEY")
    livekit_api_secret: Optional[str] = Field(default=None, alias="LIVEKIT_API_SECRET")

    # Speech Services
    stt_provider: str = Field(default="sarvam", alias="STT_PROVIDER")  # "sarvam" or "deepgram"
    tts_provider: str = Field(default="sarvam", alias="TTS_PROVIDER")  # "sarvam" or "cartesia"
    sarvam_api_key: Optional[str] = Field(default=None, alias="SARVAM_API_KEY")
    deepgram_api_key: Optional[str] = Field(default=None, alias="DEEPGRAM_API_KEY")
    cartesia_api_key: Optional[str] = Field(default=None, alias="CARTESIA_API_KEY")
    elevenlabs_api_key: Optional[str] = Field(default=None, alias="ELEVENLABS_API_KEY")

    # Database & Cache
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/voiceos",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Vector Database (Qdrant)
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")


settings = Settings()
