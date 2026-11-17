"""
Provider and service protocols for Context-Aware Suggestion RAG.

Protocols define structural contracts for interchangeable components.
Implementations can use different SDKs while exposing consistent
interfaces to the rest of the package.
"""

from typing import Protocol, Sequence, TypedDict

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.types import (
    NewsRecord,
    RetrievalResult,
    TrendRecord,
    VectorMetadata,
)


# ---------------------------------------------------------
# Vector and embedding structures
# ---------------------------------------------------------

class SparseVector(TypedDict):
    """Sparse vector representation for hybrid retrieval."""

    indices: list[int]
    values: list[float]


class VectorRecord(TypedDict):
    """Represents a vector record stored in the vector database."""

    id: str
    values: list[float]
    metadata: VectorMetadata


# ---------------------------------------------------------
# Dense embedding provider
# ---------------------------------------------------------

class DenseEmbeddingProvider(Protocol):
    """Contract for dense embedding providers."""

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """Generate dense embeddings for multiple documents."""
        ...

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        """Generate a dense embedding for a search query."""
        ...


# ---------------------------------------------------------
# Sparse embedding provider
# ---------------------------------------------------------

class SparseEmbeddingProvider(Protocol):
    """Contract for sparse embedding providers."""

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[SparseVector]:
        """Generate sparse embeddings for multiple documents."""
        ...

    def embed_query(
        self,
        text: str,
    ) -> SparseVector:
        """Generate a sparse embedding for a search query."""
        ...


# ---------------------------------------------------------
# Trend intelligence provider
# ---------------------------------------------------------

class TrendProvider(Protocol):
    """Contract for external trend intelligence providers."""

    def fetch_trends(
        self,
        keywords: Sequence[str],
        region: str,
        timeframe: str,
        limit: int,
    ) -> list[TrendRecord]:
        """Collect trend information for the requested topics."""
        ...


# ---------------------------------------------------------
# News intelligence provider
# ---------------------------------------------------------

class NewsProvider(Protocol):
    """Contract for external news collection providers."""

    def fetch_news(
        self,
        query: str,
        region: str,
        lookback_hours: int,
        limit: int,
    ) -> list[NewsRecord]:
        """Collect recent news articles matching a query."""
        ...


# ---------------------------------------------------------
# Vector database provider
# ---------------------------------------------------------

class VectorStore(Protocol):
    """Contract for vector database implementations."""

    def upsert(
        self,
        records: Sequence[VectorRecord],
        namespace: str,
    ) -> None:
        """Insert or update vector records."""
        ...

    def query(
        self,
        dense_vector: list[float],
        top_k: int,
        namespace: str,
        sparse_vector: SparseVector | None = None,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievalResult]:
        """Retrieve relevant records using dense or hybrid search."""
        ...

    def delete(
        self,
        ids: Sequence[str],
        namespace: str,
    ) -> None:
        """Delete records by their identifiers."""
        ...


# ---------------------------------------------------------
# Reranking provider
# ---------------------------------------------------------

class Reranker(Protocol):
    """Contract for search result reranking providers."""

    def rerank(
        self,
        query: str,
        results: Sequence[RetrievalResult],
        top_n: int,
    ) -> list[RetrievalResult]:
        """Rerank retrieval results according to query relevance."""
        ...


# ---------------------------------------------------------
# Large language model provider
# ---------------------------------------------------------

class LLMProvider(Protocol):
    """Contract for large language model providers."""

    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_output_tokens: int = 4096,
    ) -> str:
        """Generate text from a prompt."""
        ...


__all__ = [
    "SparseVector",
    "VectorRecord",
    "DenseEmbeddingProvider",
    "SparseEmbeddingProvider",
    "TrendProvider",
    "NewsProvider",
    "VectorStore",
    "Reranker",
    "LLMProvider",
]
