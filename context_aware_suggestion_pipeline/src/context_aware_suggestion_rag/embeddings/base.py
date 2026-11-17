"""Abstract interfaces for embedding providers."""

from abc import abstractmethod
from collections.abc import Sequence

from context_aware_suggestion_rag.core.base import BaseProvider
from context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)


class BaseDenseEmbeddingProvider(BaseProvider):
    """Interface for providers that generate dense embeddings."""

    @abstractmethod
    def embed_text(self, text: str) -> DenseEmbedding:
        """Generate a dense embedding for one text."""

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[DenseEmbedding]:
        """Generate dense embeddings for multiple texts."""

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the configured embedding dimension."""


class BaseSparseEmbeddingProvider(BaseProvider):
    """Interface for providers that generate sparse embeddings."""

    @abstractmethod
    def embed_text(self, text: str) -> SparseEmbedding:
        """Generate a sparse embedding for one text."""

    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> list[SparseEmbedding]:
        """Generate sparse embeddings for multiple texts."""
