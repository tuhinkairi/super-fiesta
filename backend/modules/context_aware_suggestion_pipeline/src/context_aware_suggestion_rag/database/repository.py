"""Repository layer for vector database operations."""

from __future__ import annotations

from typing import Any, Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.base import BaseVectorDatabase
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import DatabaseError

logger = get_logger(__name__)


class VectorRepository:
    """Provides a high-level interface for vector database operations."""

    def __init__(self, database: BaseVectorDatabase) -> None:
        if database is None:
            raise ValueError("A vector database instance is required.")

        self.database = database

    def connect(self) -> None:
        """Connect to the underlying vector database."""
        self.database.connect()

    def health_check(self) -> bool:
        """Check the underlying database health."""
        return self.database.health_check()

    def save(self, record: VectorRecord) -> DatabaseOperationResult:
        """Save a single vector record."""
        return self.save_many([record])

    def save_many(
        self,
        records: Sequence[VectorRecord],
    ) -> DatabaseOperationResult:
        """Save multiple vector records."""
        if not records:
            raise ValueError("At least one vector record is required.")

        try:
            return self.database.upsert(records)
        except Exception as exc:
            logger.exception("Failed to save vector records.")
            raise DatabaseError(
                "Could not save vector records."
            ) from exc

    def search(
        self,
        vector: list[float],
        top_k: int = 10,
        namespace: str = "default",
        metadata_filter: dict[str, Any] | None = None,
        sparse_indices: list[int] | None = None,
        sparse_values: list[float] | None = None,
    ) -> VectorQueryResult:
        """Search for similar vectors."""
        if not vector:
            raise ValueError("Query vector cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        try:
            return self.database.query(
                vector=vector,
                top_k=top_k,
                namespace=namespace,
                filter=metadata_filter,
                sparse_indices=sparse_indices,
                sparse_values=sparse_values,
            )
        except Exception as exc:
            logger.exception("Vector search failed.")
            raise DatabaseError(
                "Could not complete vector search."
            ) from exc

    def fetch(
        self,
        ids: list[str],
        namespace: str = "default",
    ) -> list[VectorRecord]:
        """Fetch vector records by their identifiers."""
        if not ids:
            return []

        try:
            return self.database.fetch(ids=ids, namespace=namespace)
        except Exception as exc:
            logger.exception("Failed to fetch vector records.")
            raise DatabaseError(
                "Could not fetch vector records."
            ) from exc

    def delete(
        self,
        ids: list[str],
        namespace: str = "default",
    ) -> DatabaseOperationResult:
        """Delete vector records by their identifiers."""
        if not ids:
            raise ValueError("At least one record ID is required.")

        try:
            return self.database.delete(
                ids=ids,
                namespace=namespace,
            )
        except Exception as exc:
            logger.exception("Failed to delete vector records.")
            raise DatabaseError(
                "Could not delete vector records."
            ) from exc

    def delete_namespace(
        self,
        namespace: str,
    ) -> DatabaseOperationResult:
        """Delete all records in a namespace."""
        if not namespace or not namespace.strip():
            raise ValueError("Namespace cannot be empty.")

        try:
            return self.database.delete_namespace(namespace)
        except Exception as exc:
            logger.exception("Failed to delete namespace.")
            raise DatabaseError(
                "Could not delete namespace."
            ) from exc

    def close(self) -> None:
        """Close the underlying database connection."""
        self.database.close()
