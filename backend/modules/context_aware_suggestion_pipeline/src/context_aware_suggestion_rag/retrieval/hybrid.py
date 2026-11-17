"""
Hybrid retrieval implementation.

Combines dense and sparse retrieval using Reciprocal Rank Fusion.
"""

from __future__ import annotations

from time import perf_counter

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import RetrievalError

from .base import BaseHybridRetriever
from .dense import DenseRetriever
from .fusion import ReciprocalRankFusion
from .models import (
    HybridRetrievalResult,
    RetrievalQuery,
    RetrievalResult,
)
from .sparse import SparseRetriever


logger = get_logger(__name__)


class HybridRetriever(BaseHybridRetriever):
    """Retrieve documents using dense and sparse retrieval together."""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        fusion: ReciprocalRankFusion | None = None,
    ) -> None:
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.fusion = fusion or ReciprocalRankFusion()

    def retrieve_hybrid(
        self,
        query: RetrievalQuery,
    ) -> HybridRetrievalResult:
        """Execute dense and sparse retrieval, then fuse their rankings."""
        if not query.use_dense or not query.use_sparse:
            raise RetrievalError(
                "Hybrid retrieval requires both use_dense and use_sparse "
                "to be True."
            )

        started_at = perf_counter()

        try:
            dense_result = self.dense_retriever.retrieve_dense(query)
            sparse_result = self.sparse_retriever.retrieve_sparse(query)

            fused_documents = self.fusion.fuse(
                dense_results=dense_result.documents,
                sparse_results=sparse_result.documents,
                top_k=query.top_k,
            )

            execution_time_ms = (perf_counter() - started_at) * 1000

            return HybridRetrievalResult(
                query=query.query,
                documents=fused_documents,
                total_matches=len(fused_documents),
                retrieval_method="hybrid",
                execution_time_ms=execution_time_ms,
                retrieved_at=dense_result.retrieved_at,
                warnings=dense_result.warnings + sparse_result.warnings,
                dense_results=dense_result.documents,
                sparse_results=sparse_result.documents,
                fusion_method="rrf",
            )

        except RetrievalError:
            raise
        except Exception as exc:
            logger.exception("Hybrid retrieval failed.")
            raise RetrievalError(
                f"Hybrid retrieval failed: {exc}"
            ) from exc

    def retrieve_many(
        self,
        queries: list[RetrievalQuery],
    ) -> list[RetrievalResult]:
        """Retrieve multiple queries sequentially."""
        return [self.retrieve_hybrid(query) for query in queries]

    def health_check(self) -> bool:
        """Check the health of both retrievers."""
        try:
            return (
                self.dense_retriever.health_check()
                and self.sparse_retriever.health_check()
            )
        except Exception:
            logger.exception("Hybrid retriever health check failed.")
            return False
