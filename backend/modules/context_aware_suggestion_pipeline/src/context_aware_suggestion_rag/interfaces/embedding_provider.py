"""
Embedding provider interfaces.

Defines common contracts for dense and sparse embedding providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)


class EmbeddingProvider(ABC):
    """Base interface for all embedding providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider connection."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError


class DenseEmbeddingProvider(EmbeddingProvider):
    """Interface for dense vector embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> DenseEmbedding:
        """Generate a dense embedding for one text."""
        raise NotImplementedError

    @abstractmethod
    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[DenseEmbedding]:
        """Generate dense embeddings for multiple texts."""
        raise NotImplementedError

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the embedding vector dimension."""
        raise NotImplementedError


class SparseEmbeddingProvider(EmbeddingProvider):
    """Interface for sparse vector embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> SparseEmbedding:
        """Generate a sparse embedding for one text."""
        raise NotImplementedError

    @abstractmethod
    def embed_texts(
        self,
        texts: Sequence[str],
    ) -> list[SparseEmbedding]:
        """Generate sparse embeddings for multiple texts."""
        raise NotImplementedError
