"""
Embedding configuration for Hybrid RAG.

Defines dense and sparse embedding providers, model identifiers,
vector dimensions, and batch processing parameters.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
import sys

AGENTS_ROOT = Path(__file__).resolve().parents[5]
if str(AGENTS_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENTS_ROOT))
from model_config import get_model_settings


class EmbeddingConfig(BaseSettings):
    """Configuration for dense and sparse embedding systems."""

    # --------------------------------------------------------
    # Dense Embeddings
    # --------------------------------------------------------

    dense_provider: Literal[
        "google",
    ] = "google"

    dense_model: str = "gemini-embedding-001"

    dense_dimension: int = Field(
        default=768,
        gt=0,
    )

    normalize_dense_embeddings: bool = True

    # --------------------------------------------------------
    # Sparse Embeddings
    # --------------------------------------------------------

    sparse_provider: Literal[
        "pinecone",
        "bm25",
    ] = "bm25"

    sparse_model: str = "pinecone-sparse-english-v0"

    # --------------------------------------------------------
    # Batch Processing
    # --------------------------------------------------------

    batch_size: int = Field(
        default=32,
        ge=1,
        le=256,
    )

    max_input_tokens: int = Field(
        default=20000,
        ge=1,
    )

    # --------------------------------------------------------
    # Retry Configuration
    # --------------------------------------------------------

    max_retries: int = Field(
        default=3,
        ge=0,
    )

    # --------------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=AGENTS_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="CASR_EMBEDDING_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )


@lru_cache(maxsize=1)
def get_embedding_config() -> EmbeddingConfig:
    """Return a cached embedding configuration instance."""

    return EmbeddingConfig(dense_model=get_model_settings().embedding_model)


__all__ = [
    "EmbeddingConfig",
    "get_embedding_config",
]
