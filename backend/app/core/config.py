from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    DEFAULT_API_PREFIX,
    DEFAULT_APP_NAME,
    DEFAULT_VERSION,
    ENV_DEV,
)


class Settings(BaseSettings):
    """
    Application Settings configured via environment variables.
    """

    APP_NAME: str = DEFAULT_APP_NAME
    APP_VERSION: str = DEFAULT_VERSION
    API_PREFIX: str = DEFAULT_API_PREFIX
    ENVIRONMENT: str = ENV_DEV
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str = "dummy-secret-key-for-local-dev-only"
    JWT_SECRET_KEY: str = "dummy-jwt-secret-key-for-local-dev-only"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # CORS & Middleware
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()  # type: ignore[call-arg]
