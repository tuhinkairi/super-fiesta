"""
Retrieval provider interfaces.

Defines a common contract for document retrieval implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.retrieval.models import (
    RetrievalQuery,
    RetrievalResult,
)


class RetrievalProvider(ABC):
    """Abstract contract for retrieval providers."""

    @abstractmethod
    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        """Retrieve relevant documents for a query."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the retrieval provider is operational."""
        raise NotImplementedError

    def retrieve_many(
        self,
        queries: Sequence[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Retrieve documents for multiple queries."""
        if isinstance(queries, (str, bytes)):
            raise TypeError("queries must be a sequence of RetrievalQuery objects")

        if not isinstance(queries, Sequence):
            raise TypeError("queries must be a sequence")

        if not all(isinstance(query, RetrievalQuery) for query in queries):
            raise TypeError("Every item must be a RetrievalQuery")

        return [self.retrieve(query) for query in queries]

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
