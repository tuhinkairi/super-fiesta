"""Factory functions for creating embedding providers and services."""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.embedding_config import (
    get_embedding_config,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.base import (
    BaseDenseEmbeddingProvider,
    BaseSparseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.dense import (
    GoogleDenseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.service import EmbeddingService
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.sparse import (
    BM25SparseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import ConfigurationError


def create_dense_embedding_provider() -> BaseDenseEmbeddingProvider:
    """Create the configured dense embedding provider."""
    config = get_embedding_config()
    provider = config.dense_provider.lower()

    if provider == "google":
        return GoogleDenseEmbeddingProvider()

    raise ConfigurationError(
        f"Unsupported dense embedding provider: {provider}"
    )


def create_sparse_embedding_provider() -> BaseSparseEmbeddingProvider:
    """Create the configured sparse embedding provider."""
    config = get_embedding_config()
    provider = config.sparse_provider.lower()

    if provider == "bm25":
        return BM25SparseEmbeddingProvider()

    raise ConfigurationError(
        f"Unsupported sparse embedding provider: {provider}"
    )


def create_embedding_service() -> EmbeddingService:
    """Create an embedding service using configured providers."""
    return EmbeddingService(
        dense_provider=create_dense_embedding_provider(),
        sparse_provider=create_sparse_embedding_provider(),
    )
