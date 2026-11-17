"""Abstract interface for vector database providers."""

from abc import abstractmethod
from collections.abc import Sequence
from typing import Any

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.base import BaseProvider
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
)


class BaseVectorDatabase(BaseProvider):
    """Contract for vector database implementations."""

    @abstractmethod
    def create_index(self) -> None:
        """Create the vector index if it does not exist."""

    @abstractmethod
    def describe_index(self) -> dict[str, Any]:
        """Return information about the configured index."""

    @abstractmethod
    def upsert(
        self,
        records: Sequence[VectorRecord],
        namespace: str | None = None,
    ) -> DatabaseOperationResult:
        """Insert or update vector records."""

    @abstractmethod
    def query(
        self,
        vector: Sequence[float],
        top_k: int = 10,
        namespace: str = "documents",
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
    ) -> VectorQueryResult:
        """Search for similar dense vectors."""

    @abstractmethod
    def delete(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> DatabaseOperationResult:
        """Delete vectors by their IDs."""

    @abstractmethod
    def delete_namespace(
        self,
        namespace: str,
    ) -> DatabaseOperationResult:
        """Delete all vectors from a namespace."""

    @abstractmethod
    def fetch(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> list[VectorRecord]:
        """Fetch vectors by their IDs."""

    @abstractmethod
    def close(self) -> None:
        """Release database resources."""
