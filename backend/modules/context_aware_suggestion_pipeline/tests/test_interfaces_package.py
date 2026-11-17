
from context_aware_suggestion_rag.interfaces import (
    AccessControlProvider,
    CacheProvider,
    DenseEmbeddingProvider,
    DocumentParser,
    EmbeddingProvider,
    GenerationProvider,
    InputSanitizer,
    IntelligenceProvider,
    LLMProvider,
    MetricsProvider,
    NewsProvider,
    NotificationProvider,
    ObservabilityProvider,
    RecommendationProvider,
    RerankerProvider,
    RetrievalProvider,
    SecurityProvider,
    SecurityValidator,
    SparseEmbeddingProvider,
    TracingProvider,
    TrendProvider,
    VectorStore,
    WorkflowProvider,
)


interfaces = [
    AccessControlProvider,
    CacheProvider,
    DenseEmbeddingProvider,
    DocumentParser,
    EmbeddingProvider,
    GenerationProvider,
    InputSanitizer,
    IntelligenceProvider,
    LLMProvider,
    MetricsProvider,
    NewsProvider,
    NotificationProvider,
    ObservabilityProvider,
    RecommendationProvider,
    RerankerProvider,
    RetrievalProvider,
    SecurityProvider,
    SecurityValidator,
    SparseEmbeddingProvider,
    TracingProvider,
    TrendProvider,
    VectorStore,
    WorkflowProvider,
]

assert len(interfaces) == 23
assert len(set(interfaces)) == 23

print("Interface package imports: PASS")
print("Interface export count: PASS")
print("All interface package exports passed.")
