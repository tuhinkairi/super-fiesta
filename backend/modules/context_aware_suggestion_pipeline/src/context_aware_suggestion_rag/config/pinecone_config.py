"""
Pinecone configuration.

Defines authentication, serverless index settings, vector dimensions,
and database configuration for the Hybrid RAG architecture.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[6] / ".env"


class PineconeConfig(BaseSettings):
    """Configuration for the Pinecone vector database."""

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    api_key: SecretStr | None = Field(
        default=None,
        validation_alias="PINECONE_API_KEY",
    )

    # --------------------------------------------------------
    # Index Configuration
    # --------------------------------------------------------

    index_name: str = Field(
        default="context-aware-suggestion-index",
        min_length=1,
    )

    dimension: int = Field(
        default=768,
        gt=0,
    )

    metric: Literal[
        "cosine",
        "dotproduct",
        "euclidean",
    ] = "dotproduct"

    # --------------------------------------------------------
    # Serverless Configuration
    # --------------------------------------------------------

    cloud: Literal[
        "aws",
        "gcp",
        "azure",
    ] = "aws"

    region: str = "us-east-1"

    # --------------------------------------------------------
    # Index Management
    # --------------------------------------------------------

    create_index_if_missing: bool = True

    deletion_protection: Literal[
        "enabled",
        "disabled",
    ] = "disabled"

    # --------------------------------------------------------
    # Connection Configuration
    # --------------------------------------------------------

    timeout_seconds: int = Field(
        default=30,
        ge=1,
    )

    max_retries: int = Field(
        default=3,
        ge=0,
    )

    # --------------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV,
        env_file_encoding="utf-8",
        env_prefix="CASR_PINECONE_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    @property
    def is_configured(self) -> bool:
        """Check whether the Pinecone API key is available."""

        return (
            self.api_key is not None
            and bool(self.api_key.get_secret_value().strip())
        )


@lru_cache(maxsize=1)
def get_pinecone_config() -> PineconeConfig:
    """Return a cached Pinecone configuration instance."""

    return PineconeConfig()


__all__ = [
    "PineconeConfig",
    "get_pinecone_config",
]
