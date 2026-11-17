"""
Retrieval configuration for Pinecone Hybrid RAG.

Defines hybrid search weights, candidate limits, reranking,
metadata filtering, and result fusion parameters.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrievalConfig(BaseSettings):
    """Configuration for the retrieval pipeline."""

    # --------------------------------------------------------
    # Hybrid Retrieval
    # --------------------------------------------------------

    retrieval_strategy: Literal[
        "dense",
        "sparse",
        "hybrid",
    ] = "hybrid"

    dense_weight: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
    )

    sparse_weight: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
    )

    # --------------------------------------------------------
    # Retrieval Limits
    # --------------------------------------------------------

    initial_top_k: int = Field(
        default=30,
        ge=1,
    )

    final_top_k: int = Field(
        default=10,
        ge=1,
    )

    minimum_relevance_score: float = Field(
        default=0.0,
        ge=0.0,
    )

    # --------------------------------------------------------
    # Reranking
    # --------------------------------------------------------

    reranking_enabled: bool = False

    reranker_provider: Literal[
        "none",
        "cohere",
        "pinecone",
    ] = "none"

    reranker_model: str | None = None

    reranker_top_n: int = Field(
        default=10,
        ge=1,
    )

    # --------------------------------------------------------
    # Result Fusion
    # --------------------------------------------------------

    fusion_strategy: Literal[
        "weighted_score",
        "reciprocal_rank",
    ] = "weighted_score"

    reciprocal_rank_constant: int = Field(
        default=60,
        ge=1,
    )

    # --------------------------------------------------------
    # Metadata Filtering
    # --------------------------------------------------------

    metadata_filtering_enabled: bool = True

    enforce_source_filter: bool = True

    enforce_expiry_filter: bool = True

    # --------------------------------------------------------
    # Retrieval Configuration
    # --------------------------------------------------------

    fetch_document_results: int = Field(
        default=10,
        ge=1,
    )

    fetch_trend_results: int = Field(
        default=10,
        ge=1,
    )

    fetch_news_results: int = Field(
        default=10,
        ge=1,
    )

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    @model_validator(mode="after")
    def validate_retrieval_settings(self):
        """Validate retrieval weights and candidate limits."""

        if self.retrieval_strategy == "hybrid":
            total_weight = self.dense_weight + self.sparse_weight

            if abs(total_weight - 1.0) > 1e-6:
                raise ValueError(
                    "Dense and sparse weights must sum to 1.0 "
                    "when hybrid retrieval is enabled."
                )

        if self.final_top_k > self.initial_top_k:
            raise ValueError(
                "final_top_k cannot exceed initial_top_k."
            )

        if self.reranker_top_n > self.initial_top_k:
            raise ValueError(
                "reranker_top_n cannot exceed initial_top_k."
            )

        if self.reranking_enabled and self.reranker_provider == "none":
            raise ValueError(
                "A reranker provider must be selected when "
                "reranking is enabled."
            )

        return self

    # --------------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CASR_RETRIEVAL_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )


@lru_cache(maxsize=1)
def get_retrieval_config() -> RetrievalConfig:
    """Return a cached retrieval configuration instance."""

    return RetrievalConfig()


__all__ = [
    "RetrievalConfig",
    "get_retrieval_config",
]
