"""
Retrieval package.

Provides dense, sparse, and hybrid retrieval, document fusion,
reranking, and retrieval service factories.
"""

from .models import (
    RetrievalQuery,
    RetrievedDocument,
    RetrievalResult,
    HybridRetrievalResult,
    RetrievalMetrics,
)

from .base import (
    BaseRetriever,
    BaseDenseRetriever,
    BaseSparseRetriever,
    BaseHybridRetriever,
)

from .dense import DenseRetriever
from .sparse import SparseRetriever
from .fusion import (
    ReciprocalRankFusion,
    reciprocal_rank_fusion,
)
from .hybrid import HybridRetriever

from .reranker import (
    BaseReranker,
    RetrievalReranker,
)

from .service import RetrievalService

from .factory import (
    create_dense_retriever,
    create_sparse_retriever,
    create_hybrid_retriever,
    create_retrieval_service,
)


__all__ = [
    # Models
    "RetrievalQuery",
    "RetrievedDocument",
    "RetrievalResult",
    "HybridRetrievalResult",
    "RetrievalMetrics",

    # Base interfaces
    "BaseRetriever",
    "BaseDenseRetriever",
    "BaseSparseRetriever",
    "BaseHybridRetriever",

    # Retrievers
    "DenseRetriever",
    "SparseRetriever",
    "HybridRetriever",

    # Fusion
    "ReciprocalRankFusion",
    "reciprocal_rank_fusion",

    # Reranking
    "BaseReranker",
    "RetrievalReranker",

    # Service
    "RetrievalService",

    # Factories
    "create_dense_retriever",
    "create_sparse_retriever",
    "create_hybrid_retriever",
    "create_retrieval_service",
]
