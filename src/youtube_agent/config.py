"""Configuración centralizada del agente."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Groq (gratuito)
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama-3.3-70b-versatile")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1")

    # YouTube OAuth2
    youtube_client_id: str = Field(default="")
    youtube_client_secret: str = Field(default="")

    # TTS
    tts_voice: str = Field(default="es-MX-JorgeNeural")

    # Video
    output_dir: Path = Field(default=Path("./output"))
    target_duration: int = Field(default=480)
    video_width: int = Field(default=1920)
    video_height: int = Field(default=1080)

    # YouTube upload
    youtube_category_id: str = Field(default="27")
    youtube_privacy: str = Field(default="public")


def get_settings() -> Settings:
    return Settings()
