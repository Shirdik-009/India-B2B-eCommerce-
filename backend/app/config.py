"""Application configuration."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_env = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_env) if _env.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "India B2B Marketplace"
    environment: str = "development"
    debug: bool = False

    # Security
    secret_key: str = "change-me-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # Database (use postgresql+asyncpg for async)
    database_url: str = "postgresql+asyncpg://marketplace:marketplace_secret@localhost:5432/marketplace"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # CORS (allow common dev origins; add more in production as needed)
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
