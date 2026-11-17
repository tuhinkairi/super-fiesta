"""
Central LangGraph state definition.

Defines the shared state passed between workflow nodes throughout
the Context-Aware Suggestion RAG pipeline.
"""

from typing import NotRequired, TypedDict

from context_aware_suggestion_rag.core.types import (
    ContextProfile,
    DocumentChunk,
    DocumentRecord,
    GeneratedContent,
    NewsRecord,
    Recommendation,
    RetrievalResult,
    TrendRecord,
    VectorMetadata,
)


class PipelineState(TypedDict):
    """
    Shared state for the complete RAG workflow.

    LangGraph nodes read from this state and return partial
    dictionaries containing the fields they update.
    """

    # -----------------------------------------------------
    # Request information
    # -----------------------------------------------------

    request_id: str
    query: str
    language: str
    region: str
    max_recommendations: int

    # -----------------------------------------------------
    # Document ingestion
    # -----------------------------------------------------

    document_ids: list[str]
    documents: NotRequired[list[DocumentRecord]]
    chunks: NotRequired[list[DocumentChunk]]

    # -----------------------------------------------------
    # Context extraction
    # -----------------------------------------------------

    context_profile: NotRequired[ContextProfile]
    extracted_topics: NotRequired[list[str]]
    extracted_keywords: NotRequired[list[str]]
    extracted_entities: NotRequired[list[str]]

    # -----------------------------------------------------
    # External intelligence
    # -----------------------------------------------------

    trends: NotRequired[list[TrendRecord]]
    news: NotRequired[list[NewsRecord]]

    # -----------------------------------------------------
    # Embedding information
    # -----------------------------------------------------

    dense_query_embedding: NotRequired[list[float]]
    sparse_query_embedding: NotRequired[dict[str, list[float] | list[int]]]

    # -----------------------------------------------------
    # Retrieval
    # -----------------------------------------------------

    retrieved_documents: NotRequired[list[RetrievalResult]]
    retrieved_trends: NotRequired[list[RetrievalResult]]
    retrieved_news: NotRequired[list[RetrievalResult]]
    retrieved_context: NotRequired[list[RetrievalResult]]

    # -----------------------------------------------------
    # Recommendations
    # -----------------------------------------------------

    recommendations: NotRequired[list[Recommendation]]

    # -----------------------------------------------------
    # Content generation
    # -----------------------------------------------------

    generated_content: NotRequired[list[GeneratedContent]]

    # -----------------------------------------------------
    # Execution information
    # -----------------------------------------------------

    current_step: NotRequired[str]
    completed_steps: NotRequired[list[str]]
    retry_count: NotRequired[int]
    errors: NotRequired[list[str]]
    warnings: NotRequired[list[str]]

    # -----------------------------------------------------
    # Additional metadata
    # -----------------------------------------------------

    metadata: NotRequired[VectorMetadata]


__all__ = [
    "PipelineState",
]
