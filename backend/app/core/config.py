from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    AEMET_API_KEY: str
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/weather.db"
    LOG_LEVEL: str = "INFO"
    APP_ENV: str = "development"
    CORS_ORIGINS: list[str] = []

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, list):
            return value
        return []


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
