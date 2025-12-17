"""
Configuration module for Physical AI & Humanoid Robotics Platform.

Loads environment variables and provides typed configuration settings.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    environment: str = Field(default="development", description="Environment mode")

    # Database (Neon PostgreSQL)
    database_url: str = Field(
        default="postgresql://localhost/humanoid_robotics",
        description="PostgreSQL connection string",
    )

    # Vector Store (Qdrant)
    qdrant_url: str = Field(
        default="http://localhost:6333",
        description="Qdrant server URL",
    )
    qdrant_api_key: str | None = Field(
        default=None,
        description="Qdrant API key for cloud",
    )
    qdrant_collection: str = Field(
        default="chapter_embeddings",
        description="Qdrant collection name",
    )

    # AI Services
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for embeddings and chat",
    )
    cohere_api_key: str | None = Field(
        default=None,
        description="Cohere API key for embeddings and chat",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for translation",
    )

    # Authentication
    better_auth_secret: str = Field(
        default="change-this-secret-in-production",
        description="BetterAuth secret key",
    )
    better_auth_url: str = Field(
        default="http://localhost:3000",
        description="BetterAuth URL",
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated CORS origins",
    )

    # Model Configuration
    embedding_model: str = Field(
        default="embed-english-v3.0",
        description="Cohere embedding model",
    )
    chat_model: str = Field(
        default="command-r-plus",
        description="Cohere chat model",
    )
    translation_model: str = Field(
        default="claude-3-haiku-20240307",
        description="Anthropic translation model",
    )

    # AI Provider selection
    ai_provider: str = Field(
        default="cohere",
        description="AI provider to use: 'openai' or 'cohere'",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
