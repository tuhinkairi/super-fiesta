"""Base interfaces for retrieval implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.retrieval.models import (
    RetrievalQuery,
    RetrievalResult,
)


class BaseRetriever(ABC):
    """Abstract base class for all retrieval implementations."""

    @abstractmethod
    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        """Retrieve relevant documents for a query."""
        raise NotImplementedError

    @abstractmethod
    def retrieve_many(
        self,
        queries: Sequence[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Retrieve results for multiple queries."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the retriever is operational."""
        raise NotImplementedError

    def close(self) -> None:
        """Release resources used by the retriever."""
        return None


class BaseDenseRetriever(BaseRetriever):
    """Interface for dense vector retrieval."""

    @abstractmethod
    def retrieve_dense(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        """Retrieve documents using dense embeddings."""
        raise NotImplementedError

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        return self.retrieve_dense(query)


class BaseSparseRetriever(BaseRetriever):
    """Interface for sparse vector retrieval."""

    @abstractmethod
    def retrieve_sparse(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        """Retrieve documents using sparse vectors."""
        raise NotImplementedError

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        return self.retrieve_sparse(query)


class BaseHybridRetriever(BaseRetriever):
    """Interface for hybrid dense and sparse retrieval."""

    @abstractmethod
    def retrieve_hybrid(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        """Retrieve documents using hybrid search."""
        raise NotImplementedError

    def retrieve(
        self,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        return self.retrieve_hybrid(query)
