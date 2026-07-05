"""Application configuration using pydantic-settings."""

from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "SynapseHR"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    APP_SECRET_KEY: str = "dev-secret-key-change-in-production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://synapsehr:synapsehr@localhost:5432/synapsehr"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT Authentication
    JWT_SECRET_KEY: str = "dev-jwt-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Configuration
    AI_PROVIDER: str = "openai"
    AI_MODEL: str = "gpt-4"
    AI_API_KEY: str = ""
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # Vector Database
    VECTOR_DB_TYPE: str = "chromadb"
    VECTOR_DB_PATH: str = "./chroma_db"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    GENERATED_DOCS_DIR: str = "./generated_documents"
    KNOWLEDGE_DIR: str = "./knowledge"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "SynapseHR"
    SMTP_FROM_EMAIL: str = "noreply@synapsehr.com"
    SMTP_USE_TLS: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:4321", "http://localhost:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AI_PER_MINUTE: int = 20

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return [origin.strip() for origin in v.split(",")]
        return v

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        if self.APP_ENV == "production":
            unsafe_defaults = {
                "APP_SECRET_KEY": "dev-secret-key-change-in-production",
                "JWT_SECRET_KEY": "dev-jwt-secret-change-in-production",
            }
            violations = [k for k, v in unsafe_defaults.items() if getattr(self, k) == v]
            if violations:
                raise ValueError(
                    f"Insecure defaults in production — set proper values for: {', '.join(violations)}"
                )
        return self

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def async_database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "")
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        return url


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
