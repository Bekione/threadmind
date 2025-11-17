from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars like ALEMBIC_SCRIPT_LOCATION
    )

    # Core
    ENV: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    TZ: str = Field(default="UTC")

    # API
    API_HOST: str = Field(default="0.0.0.0")
    API_PORT: int = Field(default=8000)
    API_WORKERS: int = Field(default=2)
    API_GATEWAY_URL: str = Field(default="http://localhost:8000")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(default="")
    BOT_POLL_INTERVAL_SECONDS: int = Field(default=3)
    BOT_POLL_TIMEOUT_SECONDS: int = Field(default=120)

    # Database
    POSTGRES_DB: str = Field(default="threadmind")
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@localhost:5432/threadmind")

    # Redis / Celery
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=10)
    RATE_LIMIT_PER_HOUR: int = Field(default=200)

    # AI Providers
    OPENAI_API_KEY: str = Field(default="")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini")

    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = Field(default="gemini-1.5-flash")

    # Telegram (Telethon) - for fetching real discussion threads
    TELEGRAM_API_ID: int = Field(default=0)
    TELEGRAM_API_HASH: str = Field(default="")
    TELEGRAM_SESSION: str = Field(default="")  # Telethon StringSession
    TELEGRAM_FETCH_LIMIT: int = Field(default=200)
    TELEGRAM_REQUIRE_REAL_FETCH: bool = Field(default=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
