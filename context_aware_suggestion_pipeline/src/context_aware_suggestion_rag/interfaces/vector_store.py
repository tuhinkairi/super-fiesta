"""
Vector store interfaces.

Defines a provider-independent contract for vector database operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
)


class VectorStore(ABC):
    """Abstract contract for vector database implementations."""

    @abstractmethod
    def connect(self) -> None:
        """Establish a database connection."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check database availability."""
        raise NotImplementedError

    @abstractmethod
    def upsert(
        self,
        records: Sequence[VectorRecord],
    ) -> DatabaseOperationResult:
        """Insert or update vector records."""
        raise NotImplementedError

    @abstractmethod
    def query(
        self,
        vector: Sequence[float],
        top_k: int = 10,
        namespace: str = "documents",
        filter: Mapping[str, Any] | None = None,
        include_metadata: bool = True,
        sparse_indices: Sequence[int] | None = None,
        sparse_values: Sequence[float] | None = None,
    ) -> VectorQueryResult:
        """Search for similar vectors."""
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> DatabaseOperationResult:
        """Delete records by ID."""
        raise NotImplementedError

    @abstractmethod
    def delete_namespace(
        self,
        namespace: str,
    ) -> DatabaseOperationResult:
        """Delete all records in a namespace."""
        raise NotImplementedError

    @abstractmethod
    def fetch(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> list[VectorRecord]:
        """Fetch records by ID."""
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        """Release database resources."""
        raise NotImplementedError
