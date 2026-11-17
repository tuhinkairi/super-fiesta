"""
Reranker provider interfaces.

Defines the contract for external document reranking providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.retrieval.models import RetrievedDocument


class RerankerProvider(ABC):
    """Abstract contract for document reranking providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider connection."""

    @abstractmethod
    def health_check(self) -> bool:
        """Return whether the provider is healthy."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: Sequence[RetrievedDocument],
        top_k: int,
    ) -> list[RetrievedDocument]:
        """
        Rerank retrieved documents against a query.

        Args:
            query: User's search query.
            documents: Documents returned by the retrieval stage.
            top_k: Maximum number of reranked documents to return.

        Returns:
            Documents ordered by reranking relevance.
        """

    def close(self) -> None:
        """Release provider resources, if any."""
