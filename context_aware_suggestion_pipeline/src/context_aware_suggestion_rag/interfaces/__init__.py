"""
Public interfaces for the Context-Aware Suggestion RAG package.

This module exposes provider-neutral contracts for the package's
core services and external integrations.
"""

from context_aware_suggestion_rag.interfaces.cache_provider import (
    CacheProvider,
)

from context_aware_suggestion_rag.interfaces.document_parser import (
    DocumentParser,
)

from context_aware_suggestion_rag.interfaces.embedding_provider import (
    DenseEmbeddingProvider,
    EmbeddingProvider,
    SparseEmbeddingProvider,
)

from context_aware_suggestion_rag.interfaces.generation_provider import (
    GenerationProvider,
)

from context_aware_suggestion_rag.interfaces.intelligence_provider import (
    IntelligenceProvider,
    NewsProvider,
    TrendProvider,
)

from context_aware_suggestion_rag.interfaces.llm_provider import (
    LLMProvider,
)

from context_aware_suggestion_rag.interfaces.notification_provider import (
    NotificationProvider,
)

from context_aware_suggestion_rag.interfaces.observability_provider import (
    MetricsProvider,
    ObservabilityProvider,
    TracingProvider,
)

from context_aware_suggestion_rag.interfaces.recommendation_provider import (
    RecommendationProvider,
)

from context_aware_suggestion_rag.interfaces.reranker_provider import (
    RerankerProvider,
)

from context_aware_suggestion_rag.interfaces.retrieval_provider import (
    RetrievalProvider,
)

from context_aware_suggestion_rag.interfaces.security_provider import (
    AccessControlProvider,
    InputSanitizer,
    SecurityProvider,
    SecurityValidator,
)

from context_aware_suggestion_rag.interfaces.vector_store import (
    VectorStore,
)

from context_aware_suggestion_rag.interfaces.workflow_provider import (
    WorkflowProvider,
)


__all__ = [
    "AccessControlProvider",
    "CacheProvider",
    "DenseEmbeddingProvider",
    "DocumentParser",
    "EmbeddingProvider",
    "GenerationProvider",
    "InputSanitizer",
    "IntelligenceProvider",
    "LLMProvider",
    "MetricsProvider",
    "NewsProvider",
    "NotificationProvider",
    "ObservabilityProvider",
    "RecommendationProvider",
    "RerankerProvider",
    "RetrievalProvider",
    "SecurityProvider",
    "SecurityValidator",
    "SparseEmbeddingProvider",
    "TracingProvider",
    "TrendProvider",
    "VectorStore",
    "WorkflowProvider",
]
