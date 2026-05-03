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

    # xAI (Grok)
    xai_api_key: str = Field(default="")
    xai_model: str = Field(default="grok-3")
    xai_image_model: str = Field(default="grok-2-image")
    xai_base_url: str = Field(default="https://api.x.ai/v1")

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
