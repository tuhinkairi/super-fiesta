"""Pinecone vector database implementation."""

from collections import defaultdict
from collections.abc import Sequence
from typing import Any

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.database.base import BaseVectorDatabase
from context_aware_suggestion_rag.database.connection import (
    PineconeConnection,
)
from context_aware_suggestion_rag.database.index_manager import (
    PineconeIndexManager,
)
from context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorQueryResult,
    VectorRecord,
    VectorSearchResult,
)
from context_aware_suggestion_rag.exceptions import (
    DatabaseError,
    PineconeConnectionError,
)

logger = get_logger(__name__)


class PineconeVectorStore(BaseVectorDatabase):
    """Store and retrieve dense or hybrid vectors using Pinecone."""

    def __init__(
        self,
        connection: PineconeConnection | None = None,
        index_manager: PineconeIndexManager | None = None,
    ) -> None:
        self.connection = connection or PineconeConnection()
        self.index_manager = index_manager or PineconeIndexManager(
            self.connection
        )
        self._index: Any | None = None

    def connect(self) -> None:
        """Connect to the Pinecone index."""
        try:
            self.index_manager.ensure_index()
            self._index = self.connection.get_index()
            logger.info("Connected to Pinecone vector index.")
        except Exception as exc:
            logger.exception("Failed to connect to Pinecone.")
            raise PineconeConnectionError(
                "Failed to connect to Pinecone vector index."
            ) from exc


    def health_check(self) -> bool:
        """Check whether the Pinecone vector store is operational."""
        try:
            index = self._get_index()
            stats = index.describe_index_stats()
            return stats is not None
        except Exception:
            logger.exception("Pinecone vector store health check failed.")
            return False
    
    def _get_index(self) -> Any:
        """Return the active index, connecting if necessary."""
        if self._index is None:
            self.connect()

        return self._index

    def create_index(self) -> None:
        """Create the configured index if necessary."""
        self.index_manager.ensure_index()
        self._index = self.connection.get_index()

    def describe_index(self) -> dict[str, Any]:
        """Return information about the configured index."""
        return self.index_manager.describe_index()

    @staticmethod
    def _vector_payload(record: VectorRecord) -> dict[str, Any]:
        """Convert a VectorRecord into a Pinecone vector payload."""
        payload: dict[str, Any] = {
            "id": record.id,
            "values": record.values,
            "metadata": record.metadata,
        }

        if record.sparse_indices is not None:
            payload["sparse_values"] = {
                "indices": record.sparse_indices,
                "values": record.sparse_values,
            }

        return payload

    def upsert(
        self,
        records: Sequence[VectorRecord],
        namespace: str | None = None,
    ) -> DatabaseOperationResult:
        """Insert or update dense and optional sparse vectors."""
        if not records:
            return DatabaseOperationResult(
                success=True,
                operation="upsert",
                affected_count=0,
                message="No records supplied.",
            )

        index = self._get_index()

        # Group records because Pinecone accepts one namespace per upsert.
        grouped_records: dict[str, list[VectorRecord]] = defaultdict(list)

        for record in records:
            target_namespace = namespace or record.namespace
            grouped_records[target_namespace].append(record)

        affected_count = 0

        try:
            for target_namespace, group in grouped_records.items():
                response = index.upsert(
                    vectors=[
                        self._vector_payload(record)
                        for record in group
                    ],
                    namespace=target_namespace,
                )

                count = getattr(response, "upserted_count", None)

                if count is None and isinstance(response, dict):
                    count = response.get("upserted_count")

                affected_count += (
                    int(count) if count is not None else len(group)
                )

            return DatabaseOperationResult(
                success=True,
                operation="upsert",
                affected_count=affected_count,
                message="Vectors upserted successfully.",
            )

        except Exception as exc:
            raise DatabaseError(
                f"Pinecone upsert failed: {exc}"
            ) from exc

    def query(
        self,
        vector: Sequence[float],
        top_k: int = 10,
        namespace: str = "documents",
        filter: dict[str, Any] | None = None,
        include_metadata: bool = True,
        sparse_indices: Sequence[int] | None = None,
        sparse_values: Sequence[float] | None = None,
    ) -> VectorQueryResult:
        """Search using dense vectors and optional sparse vectors."""
        if not vector:
            raise ValueError("Query vector cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if (sparse_indices is None) != (sparse_values is None):
            raise ValueError(
                "Sparse indices and values must both be supplied."
            )

        if sparse_indices is not None:
            if len(sparse_indices) != len(sparse_values or []):
                raise ValueError(
                    "Sparse indices and values must have equal lengths."
                )

        index = self._get_index()

        query_arguments: dict[str, Any] = {
            "vector": [float(value) for value in vector],
            "top_k": top_k,
            "namespace": namespace,
            "include_metadata": include_metadata,
            "include_values": False,
        }

        if filter is not None:
            query_arguments["filter"] = filter

        if sparse_indices is not None:
            query_arguments["sparse_vector"] = {
                "indices": list(sparse_indices),
                "values": [float(value) for value in sparse_values or []],
            }

        try:
            response = index.query(**query_arguments)
            raw_matches = getattr(response, "matches", None)

            if raw_matches is None and isinstance(response, dict):
                raw_matches = response.get("matches", [])

            matches: list[VectorSearchResult] = []

            for item in raw_matches or []:
                if isinstance(item, dict):
                    get_value = item.get
                else:
                    get_value = lambda key, default=None: getattr(
                        item, key, default
                    )

                metadata = get_value("metadata", {}) or {}

                matches.append(
                    VectorSearchResult(
                        id=get_value("id", ""),
                        score=float(get_value("score", 0.0) or 0.0),
                        metadata=dict(metadata),
                        values=get_value("values"),
                    )
                )

            return VectorQueryResult(
                matches=matches,
                namespace=namespace,
                total_matches=len(matches),
            )

        except Exception as exc:
            raise DatabaseError(
                f"Pinecone query failed: {exc}"
            ) from exc

    def delete(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> DatabaseOperationResult:
        """Delete vectors by their IDs."""
        if not ids:
            return DatabaseOperationResult(
                success=True,
                operation="delete",
                affected_count=0,
                message="No vector IDs supplied.",
            )

        index = self._get_index()

        try:
            index.delete(
                ids=list(ids),
                namespace=namespace,
            )

            return DatabaseOperationResult(
                success=True,
                operation="delete",
                affected_count=len(ids),
                message="Vector deletion request submitted.",
            )

        except Exception as exc:
            raise DatabaseError(
                f"Pinecone deletion failed: {exc}"
            ) from exc

    def delete_namespace(
        self,
        namespace: str,
    ) -> DatabaseOperationResult:
        """Delete all vectors in a namespace."""
        if not namespace.strip():
            raise ValueError("Namespace cannot be empty.")

        index = self._get_index()

        try:
            index.delete(
                delete_all=True,
                namespace=namespace,
            )

            return DatabaseOperationResult(
                success=True,
                operation="delete_namespace",
                message=f"Deletion requested for namespace '{namespace}'.",
            )

        except Exception as exc:
            raise DatabaseError(
                f"Namespace deletion failed: {exc}"
            ) from exc

    def fetch(
        self,
        ids: Sequence[str],
        namespace: str = "documents",
    ) -> list[VectorRecord]:
        """Fetch vectors by their IDs."""
        if not ids:
            return []

        index = self._get_index()

        try:
            response = index.fetch(
                ids=list(ids),
                namespace=namespace,
            )

            raw_vectors = getattr(response, "vectors", None)

            if raw_vectors is None and isinstance(response, dict):
                raw_vectors = response.get("vectors", {})

            results: list[VectorRecord] = []

            for vector_id, item in (raw_vectors or {}).items():
                if isinstance(item, dict):
                    get_value = item.get
                else:
                    get_value = lambda key, default=None: getattr(
                        item, key, default
                    )

                values = get_value("values", [])
                metadata = get_value("metadata", {}) or {}
                sparse = get_value("sparse_values")

                sparse_indices = None
                sparse_values = None

                if sparse is not None:
                    if isinstance(sparse, dict):
                        sparse_indices = sparse.get("indices", [])
                        sparse_values = sparse.get("values", [])
                    else:
                        sparse_indices = getattr(sparse, "indices", [])
                        sparse_values = getattr(sparse, "values", [])

                results.append(
                    VectorRecord(
                        id=vector_id,
                        values=list(values or []),
                        metadata=dict(metadata),
                        sparse_indices=sparse_indices,
                        sparse_values=sparse_values,
                        namespace=namespace,
                    )
                )

            return results

        except Exception as exc:
            raise DatabaseError(
                f"Pinecone fetch failed: {exc}"
            ) from exc

    def close(self) -> None:
        """Release local Pinecone connection references."""
        self._index = None
        self.connection.close()

        logger.info("Pinecone vector store closed.")
