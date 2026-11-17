"""
Factories for constructing retrieval components.
"""

from __future__ import annotations

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.base import BaseVectorDatabase
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.embeddings.service import EmbeddingService

from .dense import DenseRetriever
from .fusion import ReciprocalRankFusion
from .hybrid import HybridRetriever
from .reranker import RetrievalReranker
from .service import RetrievalService
from .sparse import SparseRetriever


def create_dense_retriever(
    embedding_service: EmbeddingService,
    database: BaseVectorDatabase,
) -> DenseRetriever:
    """Create a dense-vector retriever."""
    return DenseRetriever(
        embedding_service=embedding_service,
        database=database,
    )


def create_sparse_retriever(
    embedding_service: EmbeddingService,
    database: BaseVectorDatabase,
) -> SparseRetriever:
    """Create a sparse-vector retriever."""
    return SparseRetriever(
        embedding_service=embedding_service,
        database=database,
    )


def create_hybrid_retriever(
    dense_retriever: DenseRetriever,
    sparse_retriever: SparseRetriever,
    rrf_constant: int = 60,
    dense_weight: float = 0.7,
    sparse_weight: float = 0.3,
) -> HybridRetriever:
    """Create a hybrid retriever with Reciprocal Rank Fusion."""
    fusion = ReciprocalRankFusion(
        rrf_constant=rrf_constant,
        dense_weight=dense_weight,
        sparse_weight=sparse_weight,
    )

    return HybridRetriever(
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        fusion=fusion,
    )


def create_retrieval_service(
    embedding_service: EmbeddingService,
    database: BaseVectorDatabase,
    reranker: RetrievalReranker | None = None,
    rrf_constant: int = 60,
    dense_weight: float = 0.7,
    sparse_weight: float = 0.3,
) -> RetrievalService:
    """
    Create the complete retrieval service.

    Args:
        embedding_service: Shared dense and sparse embedding service.
        database: Connected or lazily connectable vector database.
        reranker: Optional configured reranking service.
        rrf_constant: Reciprocal Rank Fusion constant.
        dense_weight: Dense contribution to RRF.
        sparse_weight: Sparse contribution to RRF.

    Returns:
        Configured RetrievalService.
    """
    dense_retriever = create_dense_retriever(
        embedding_service=embedding_service,
        database=database,
    )

    sparse_retriever = create_sparse_retriever(
        embedding_service=embedding_service,
        database=database,
    )

    hybrid_retriever = create_hybrid_retriever(
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        rrf_constant=rrf_constant,
        dense_weight=dense_weight,
        sparse_weight=sparse_weight,
    )

    return RetrievalService(
        dense_retriever=dense_retriever,
        sparse_retriever=sparse_retriever,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
    )
