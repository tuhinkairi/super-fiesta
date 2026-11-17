"""Service for coordinating dense and sparse embedding providers."""

from collections.abc import Sequence

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.base import (
    BaseDenseEmbeddingProvider,
    BaseSparseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.dense import (
    GoogleDenseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.models import (
    DenseEmbedding,
    SparseEmbedding,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.sparse import (
    BM25SparseEmbeddingProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import EmbeddingError

logger = get_logger(__name__)


class EmbeddingService:
    """Coordinate dense and sparse embedding generation."""

    def __init__(
        self,
        dense_provider: BaseDenseEmbeddingProvider | None = None,
        sparse_provider: BaseSparseEmbeddingProvider | None = None,
    ) -> None:
        self.dense_provider = (
            dense_provider or GoogleDenseEmbeddingProvider()
        )
        self.sparse_provider = (
            sparse_provider or BM25SparseEmbeddingProvider()
        )

    def embed_dense(self, text: str) -> DenseEmbedding:
        """Generate a dense embedding for one text."""
        return self.dense_provider.embed_text(text)

    def embed_sparse(self, text: str) -> SparseEmbedding:
        """Generate a sparse embedding for one text."""
        return self.sparse_provider.embed_text(text)

    def embed_dense_batch(
        self,
        texts: Sequence[str],
    ) -> list[DenseEmbedding]:
        """Generate dense embeddings for multiple texts."""
        return self.dense_provider.embed_texts(texts)

    def embed_sparse_batch(
        self,
        texts: Sequence[str],
    ) -> list[SparseEmbedding]:
        """Generate sparse embeddings for multiple texts."""
        return self.sparse_provider.embed_texts(texts)

    def embed_hybrid(
        self,
        text: str,
    ) -> tuple[DenseEmbedding, SparseEmbedding]:
        """Generate dense and sparse embeddings for one text."""
        dense = self.embed_dense(text)
        sparse = self.embed_sparse(text)
        return dense, sparse

    def embed_hybrid_batch(
        self,
        texts: Sequence[str],
    ) -> list[tuple[DenseEmbedding, SparseEmbedding]]:
        """Generate both representations for multiple texts."""
        if not texts:
            return []

        dense_results = self.embed_dense_batch(texts)
        sparse_results = self.embed_sparse_batch(texts)

        if len(dense_results) != len(texts):
            raise EmbeddingError(
                "Dense provider returned an unexpected result count."
            )

        if len(sparse_results) != len(texts):
            raise EmbeddingError(
                "Sparse provider returned an unexpected result count."
            )

        return list(zip(dense_results, sparse_results))

    def health_check(self) -> dict[str, bool]:
        """Check the health of both providers."""
        results: dict[str, bool] = {}

        try:
            self.dense_provider.connect()
            results["dense"] = self.dense_provider.health_check()
        except Exception:
            logger.exception("Dense embedding provider health check failed.")
            results["dense"] = False

        try:
            self.sparse_provider.connect()
            results["sparse"] = self.sparse_provider.health_check()
        except Exception:
            logger.exception("Sparse embedding provider health check failed.")
            results["sparse"] = False

        return results

    def close(self) -> None:
        """Close providers that expose a close method."""
        for provider in (self.dense_provider, self.sparse_provider):
            close_method = getattr(provider, "close", None)

            if callable(close_method):
                close_method()
