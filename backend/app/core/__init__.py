"""
Application configuration using pydantic-settings.
Loads from environment variables and .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./parcelhub.db"

    # Tracking Providers
    seventeen_track_api_key: str = ""
    tracking_provider: str = "mock"  # "mock" | "17track"

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # App
    app_env: str = "development"
    log_level: str = "INFO"

    # Polling intervals (minutes)
    polling_interval_active_minutes: int = 120
    polling_interval_stale_minutes: int = 720

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance. Call once at startup."""
    return Settings()
