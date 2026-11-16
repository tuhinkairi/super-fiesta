"""
Document reranking interfaces and service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.exceptions import RetrievalError

from .models import RetrievedDocument


logger = get_logger(__name__)


class BaseReranker(ABC):
    """Abstract interface for document reranking providers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: list[RetrievedDocument],
        top_k: int | None = None,
    ) -> list[RetrievedDocument]:
        """Reorder documents according to their relevance to a query."""

    def health_check(self) -> bool:
        """Return whether the reranker is available."""
        return True

    def close(self) -> None:
        """Release provider resources if necessary."""


class RetrievalReranker:
    """Apply a configured reranking provider to retrieved documents."""

    def __init__(self, provider: BaseReranker) -> None:
        self.provider = provider

    def rerank(
        self,
        query: str,
        documents: list[RetrievedDocument],
        top_k: int | None = None,
    ) -> list[RetrievedDocument]:
        """
        Rerank documents and normalize their output ranks.

        Args:
            query: Original user query.
            documents: Documents returned by retrieval.
            top_k: Maximum number of documents to return.

        Returns:
            Reranked documents with updated rank values.
        """
        if not isinstance(query, str) or not query.strip():
            raise RetrievalError("Reranking query cannot be empty.")

        if top_k is not None:
            if (
                not isinstance(top_k, int)
                or isinstance(top_k, bool)
                or top_k <= 0
            ):
                raise RetrievalError("top_k must be a positive integer.")

        if not documents:
            return []

        try:
            ranked_documents = self.provider.rerank(
                query=query,
                documents=documents,
                top_k=top_k,
            )

            if not isinstance(ranked_documents, list):
                raise RetrievalError(
                    "Reranking provider must return a list of documents."
                )

            if not all(
                isinstance(document, RetrievedDocument)
                for document in ranked_documents
            ):
                raise RetrievalError(
                    "Reranking provider returned an invalid document."
                )

            if top_k is not None:
                ranked_documents = ranked_documents[:top_k]

            return [
                RetrievedDocument(
                    id=document.id,
                    content=document.content,
                    score=document.score,
                    metadata=dict(document.metadata),
                    namespace=document.namespace,
                    source_type=document.source_type,
                    rank=rank,
                )
                for rank, document in enumerate(ranked_documents, start=1)
            ]

        except RetrievalError:
            raise
        except Exception as exc:
            logger.exception("Document reranking failed.")
            raise RetrievalError(
                f"Document reranking failed: {exc}"
            ) from exc

    def health_check(self) -> bool:
        """Check whether the configured reranking provider is healthy."""
        try:
            return bool(self.provider.health_check())
        except Exception:
            logger.exception("Reranker health check failed.")
            return False

    def close(self) -> None:
        """Close the configured reranking provider."""
        self.provider.close()
