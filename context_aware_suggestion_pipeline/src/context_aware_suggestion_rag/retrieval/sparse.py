"""
Sparse-vector retrieval implementation.

Converts a text query into a sparse embedding and searches the vector
database using sparse-vector similarity.
"""

from __future__ import annotations

from time import perf_counter
from typing import Any

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.database.base import BaseVectorDatabase
from context_aware_suggestion_rag.embeddings.service import EmbeddingService
from context_aware_suggestion_rag.exceptions import RetrievalError

from .base import BaseSparseRetriever
from .models import (
    RetrievalQuery,
    RetrievalResult,
    RetrievedDocument,
    current_utc_time,
)


logger = get_logger(__name__)


class SparseRetriever(BaseSparseRetriever):
    """Retrieve documents using sparse-vector similarity."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        database: BaseVectorDatabase,
    ) -> None:
        self.embedding_service = embedding_service
        self.database = database

    def retrieve_sparse(self, query: RetrievalQuery) -> RetrievalResult:
        """
        Embed the query sparsely and retrieve matching documents.

        Pinecone hybrid indexes require a dense vector alongside a sparse
        vector. This implementation supplies a zero-valued dense vector
        matching the configured index dimension.

        Args:
            query: Retrieval configuration and query text.

        Returns:
            RetrievalResult containing matching documents.

        Raises:
            RetrievalError: If embedding or database retrieval fails.
        """
        if not query.use_sparse:
            raise RetrievalError(
                "Sparse retrieval was requested for a query with use_sparse=False."
            )

        started_at = perf_counter()

        try:
            sparse_embedding = self.embedding_service.embed_sparse(query.query)

            index_description = self.database.describe_index()

            dimension = self._get_index_dimension(index_description)

            database_result = self.database.query(
                vector=[0.0] * dimension,
                sparse_indices=sparse_embedding.indices,
                sparse_values=sparse_embedding.values,
                top_k=query.top_k,
                namespace=query.namespace,
                filter=query.metadata_filter,
                include_metadata=True,
            )

            documents = self._convert_matches(database_result.matches)

            execution_time_ms = (perf_counter() - started_at) * 1000

            return RetrievalResult(
                query=query.query,
                documents=documents,
                total_matches=getattr(
                    database_result,
                    "total_matches",
                    len(documents),
                ),
                retrieval_method="sparse",
                execution_time_ms=execution_time_ms,
                retrieved_at=current_utc_time(),
                warnings=[],
            )

        except RetrievalError:
            raise
        except Exception as exc:
            logger.exception("Sparse retrieval failed.")
            raise RetrievalError(
                f"Sparse retrieval failed: {exc}"
            ) from exc

    def retrieve_many(
        self,
        queries: list[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Retrieve results for multiple queries sequentially."""
        return [self.retrieve_sparse(query) for query in queries]

    def health_check(self) -> bool:
        """Check whether the embedding service and database are healthy."""
        try:
            embedding_status = self.embedding_service.health_check()
            database_status = self.database.health_check()

            if isinstance(embedding_status, dict):
                embedding_healthy = all(embedding_status.values())
            else:
                embedding_healthy = bool(embedding_status)

            return embedding_healthy and bool(database_status)

        except Exception:
            logger.exception("Sparse retriever health check failed.")
            return False

    @staticmethod
    def _get_index_dimension(description: Any) -> int:
        """Extract and validate the dense dimension from index information."""
        dimension = getattr(description, "dimension", None)

        if dimension is None and isinstance(description, dict):
            dimension = description.get("dimension")

        if isinstance(description, dict) and "dimension" not in description:
            dimension = description.get("spec", {}).get("dimension")

        if not isinstance(dimension, int) or isinstance(dimension, bool):
            raise RetrievalError(
                "Could not determine the Pinecone index dimension."
            )

        if dimension <= 0:
            raise RetrievalError(
                "Pinecone index dimension must be positive."
            )

        return dimension

    @staticmethod
    def _convert_matches(matches: list[Any]) -> list[RetrievedDocument]:
        """Convert database matches into RetrievedDocument objects."""
        documents: list[RetrievedDocument] = []

        for rank, match in enumerate(matches, start=1):
            metadata = dict(match.metadata or {})

            content = (
                metadata.get("content")
                or metadata.get("text")
                or metadata.get("chunk_text")
                or metadata.get("page_content")
                or ""
            )

            documents.append(
                RetrievedDocument(
                    id=str(match.id),
                    content=str(content),
                    score=float(match.score),
                    metadata=metadata,
                    namespace=str(metadata.get("namespace", "documents")),
                    source_type=str(metadata.get("source_type", "document")),
                    rank=rank,
                )
            )

        return documents
