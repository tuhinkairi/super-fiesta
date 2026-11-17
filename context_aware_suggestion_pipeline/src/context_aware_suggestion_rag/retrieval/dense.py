"""Dense-vector retrieval implementation."""

from __future__ import annotations

from time import perf_counter
from typing import Any, Sequence

from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.database.base import BaseVectorDatabase
from context_aware_suggestion_rag.embeddings.service import EmbeddingService
from context_aware_suggestion_rag.exceptions import RetrievalError

from .base import BaseDenseRetriever
from .models import RetrievalQuery, RetrievalResult, RetrievedDocument

logger = get_logger(__name__)


class DenseRetriever(BaseDenseRetriever):
    """Retrieve documents using dense vector similarity."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        database: BaseVectorDatabase,
    ) -> None:
        self.embedding_service = embedding_service
        self.database = database

    def retrieve_dense(self, query: RetrievalQuery) -> RetrievalResult:
        """Embed a query and retrieve its nearest dense-vector matches."""
        started_at = perf_counter()
        warnings: list[str] = []

        try:
            embedding = self.embedding_service.embed_dense(query.query)

            vector_result = self.database.query(
                vector=embedding.values,
                top_k=query.top_k,
                namespace=query.namespace,
                filter=query.metadata_filter,
                include_metadata=True,
            )

            documents: list[RetrievedDocument] = []

            for rank, match in enumerate(vector_result.matches, start=1):
                metadata = dict(match.metadata or {})

                content = metadata.get("content")
                if not isinstance(content, str):
                    content = metadata.get("text", "")

                if not isinstance(content, str):
                    content = ""

                source_type = metadata.get("source_type", "document")
                if not isinstance(source_type, str):
                    source_type = "document"

                documents.append(
                    RetrievedDocument(
                        id=match.id,
                        content=content,
                        score=float(match.score),
                        metadata=metadata,
                        namespace=query.namespace,
                        source_type=source_type,
                        rank=rank,
                    )
                )

            if not documents:
                warnings.append("No matching documents were found.")

            elapsed_ms = (perf_counter() - started_at) * 1000

            return RetrievalResult(
                query=query.query,
                documents=documents,
                total_matches=vector_result.total_matches,
                retrieval_method="dense",
                execution_time_ms=elapsed_ms,
                warnings=warnings,
            )

        except RetrievalError:
            raise
        except Exception as exc:
            logger.exception("Dense retrieval failed.")
            raise RetrievalError(
                f"Dense retrieval failed: {exc}"
            ) from exc

    def retrieve_many(
        self,
        queries: Sequence[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Retrieve results for multiple queries."""
        return [self.retrieve_dense(query) for query in queries]

    def health_check(self) -> bool:
        """Check whether the embedding service and database are healthy."""
        try:
            embedding_healthy = self.embedding_service.health_check()
            database_healthy = self.database.health_check()

            return bool(embedding_healthy and database_healthy)

        except Exception:
            logger.exception("Dense retriever health check failed.")
            return False
