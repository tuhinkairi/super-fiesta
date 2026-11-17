"""
Central retrieval service.

Selects dense, sparse, or hybrid retrieval based on the query
configuration and optionally applies document reranking.
"""

from __future__ import annotations

from dataclasses import replace

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import RetrievalError

from .dense import DenseRetriever
from .hybrid import HybridRetriever
from .models import RetrievalQuery, RetrievalResult
from .reranker import RetrievalReranker
from .sparse import SparseRetriever


logger = get_logger(__name__)


class RetrievalService:
    """Coordinate retrieval strategies and optional reranking."""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        hybrid_retriever: HybridRetriever,
        reranker: RetrievalReranker | None = None,
    ) -> None:
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.hybrid_retriever = hybrid_retriever
        self.reranker = reranker

    def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        """
        Execute the retrieval strategy requested by the query.

        Strategy selection:
        - use_dense=True and use_sparse=True: hybrid
        - use_dense=True and use_sparse=False: dense
        - use_dense=False and use_sparse=True: sparse
        """
        try:
            if query.use_dense and query.use_sparse:
                result = self.hybrid_retriever.retrieve_hybrid(query)

            elif query.use_dense:
                result = self.dense_retriever.retrieve_dense(query)

            elif query.use_sparse:
                result = self.sparse_retriever.retrieve_sparse(query)

            else:
                raise RetrievalError(
                    "At least one retrieval strategy must be enabled."
                )

            if query.rerank:
                if self.reranker is None:
                    raise RetrievalError(
                        "Reranking was requested, but no reranker is configured."
                    )

                reranked_documents = self.reranker.rerank(
                    query=query.query,
                    documents=result.documents,
                    top_k=query.top_k,
                )

                result = replace(
                    result,
                    documents=reranked_documents,
                    total_matches=len(reranked_documents),
                )

            return result

        except RetrievalError:
            raise
        except Exception as exc:
            logger.exception("Retrieval service failed.")
            raise RetrievalError(
                f"Retrieval service failed: {exc}"
            ) from exc

    def retrieve_many(
        self,
        queries: list[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Execute multiple retrieval requests sequentially."""
        return [self.retrieve(query) for query in queries]

    def health_check(self) -> bool:
        """Check the health of configured retrieval components."""
        try:
            retrievers_healthy = (
                self.dense_retriever.health_check()
                and self.sparse_retriever.health_check()
                and self.hybrid_retriever.health_check()
            )

            if not retrievers_healthy:
                return False

            if self.reranker is not None:
                return self.reranker.health_check()

            return True

        except Exception:
            logger.exception("Retrieval service health check failed.")
            return False

    def close(self) -> None:
        """Close retrieval and reranking resources."""
        errors: list[Exception] = []

        components = [
            self.dense_retriever,
            self.sparse_retriever,
            self.hybrid_retriever,
        ]

        if self.reranker is not None:
            components.append(self.reranker)

        for component in components:
            close_method = getattr(component, "close", None)

            if callable(close_method):
                try:
                    close_method()
                except Exception as exc:
                    errors.append(exc)

        if errors:
            raise RetrievalError(
                f"Failed to close {len(errors)} retrieval component(s)."
            ) from errors[0]
