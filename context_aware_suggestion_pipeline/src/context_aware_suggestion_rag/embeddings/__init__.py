"""Embedding providers, models, factories, and services."""

from context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)
from context_aware_suggestion_rag.embeddings.base import (
    BaseDenseEmbeddingProvider,
    BaseSparseEmbeddingProvider,
)
from context_aware_suggestion_rag.embeddings.dense import (
    GoogleDenseEmbeddingProvider,
)
from context_aware_suggestion_rag.embeddings.sparse import (
    BM25SparseEmbeddingProvider,
)
from context_aware_suggestion_rag.embeddings.service import EmbeddingService
from context_aware_suggestion_rag.embeddings.factory import (
    create_dense_embedding_provider,
    create_sparse_embedding_provider,
    create_embedding_service,
)

__all__ = [
    "DenseEmbedding",
    "SparseEmbedding",
    "BaseDenseEmbeddingProvider",
    "BaseSparseEmbeddingProvider",
    "GoogleDenseEmbeddingProvider",
    "BM25SparseEmbeddingProvider",
    "EmbeddingService",
    "create_dense_embedding_provider",
    "create_sparse_embedding_provider",
    "create_embedding_service",
]
