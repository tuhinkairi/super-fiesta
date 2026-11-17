"""
Shared type definitions for Context-Aware Suggestion RAG.

These types establish consistent data structures across document
ingestion, context extraction, intelligence collection, retrieval,
recommendation, and content generation.
"""

from typing import NotRequired, TypeAlias, TypedDict


# ---------------------------------------------------------
# Common metadata types
# ---------------------------------------------------------

MetadataValue: TypeAlias = str | int | float | bool | list[str]

VectorMetadata: TypeAlias = dict[str, MetadataValue]


# ---------------------------------------------------------
# Document types
# ---------------------------------------------------------

class DocumentRecord(TypedDict):
    """Represents a loaded source document."""

    document_id: str
    filename: str
    file_type: str
    content: str
    metadata: NotRequired[VectorMetadata]


class DocumentChunk(TypedDict):
    """Represents a processed document chunk."""

    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Trend intelligence types
# ---------------------------------------------------------

class TrendRecord(TypedDict):
    """Represents a collected trend."""

    trend_id: str
    title: str
    region: str
    timeframe: str
    collected_at: str
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# News intelligence types
# ---------------------------------------------------------

class NewsRecord(TypedDict):
    """Represents a collected news article."""

    news_id: str
    title: str
    url: str
    source_name: str
    published_at: str | None
    summary: str
    collected_at: str
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Context types
# ---------------------------------------------------------

class ContextProfile(TypedDict):
    """Represents the combined contextual information."""

    topics: list[str]
    keywords: list[str]
    entities: list[str]
    document_summaries: list[str]
    trend_topics: list[str]
    news_topics: list[str]
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Retrieval types
# ---------------------------------------------------------

class RetrievalResult(TypedDict):
    """Represents a document, trend, or news retrieval result."""

    result_id: str
    content: str
    score: float
    source_type: str
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Recommendation types
# ---------------------------------------------------------

class Recommendation(TypedDict):
    """Represents an actionable content recommendation."""

    recommendation_id: str
    title: str
    description: str
    rationale: str
    source_ids: list[str]
    content_format: str
    priority: str
    confidence: NotRequired[float]
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Generated content types
# ---------------------------------------------------------

class GeneratedContent(TypedDict):
    """Represents content generated from a recommendation."""

    recommendation_id: str
    title: str
    body: str
    content_format: str
    metadata: NotRequired[VectorMetadata]


# ---------------------------------------------------------
# Pipeline input and output types
# ---------------------------------------------------------

class PipelineInput(TypedDict):
    """Represents the input received by the RAG pipeline."""

    request_id: str
    query: str
    document_ids: list[str]
    language: str
    region: str
    max_recommendations: int
    context: NotRequired[ContextProfile]
    metadata: NotRequired[VectorMetadata]


class PipelineOutput(TypedDict):
    """Represents the final pipeline response."""

    request_id: str
    recommendations: list[Recommendation]
    generated_content: list[GeneratedContent]
    retrieved_context: list[RetrievalResult]
    metadata: NotRequired[VectorMetadata]


__all__ = [
    "MetadataValue",
    "VectorMetadata",
    "DocumentRecord",
    "DocumentChunk",
    "TrendRecord",
    "NewsRecord",
    "ContextProfile",
    "RetrievalResult",
    "Recommendation",
    "GeneratedContent",
    "PipelineInput",
    "PipelineOutput",
]
