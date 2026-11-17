"""
Domain factories.

Centralizes the creation of domain entities and ensures
consistent defaults across the pipeline.
"""

from context_aware_suggestion_rag.core.identifiers import (
    generate_chunk_id,
    generate_content_id,
)
from context_aware_suggestion_rag.domain.entities import (
    DocumentChunkEntity,
    DocumentEntity,
    GeneratedContentEntity,
    NewsEntity,
    RecommendationEntity,
    TrendEntity,
)
from context_aware_suggestion_rag.domain.enums import (
    ContentFormat,
    DocumentType,
    RecommendationPriority,
)


def create_document(
    filename: str,
    document_type: DocumentType,
    content: str,
    **kwargs,
) -> DocumentEntity:
    """Create a validated document entity."""
    return DocumentEntity(
        filename=filename,
        document_type=document_type,
        content=content,
        **kwargs,
    )


def create_document_chunk(
    document_id: str,
    content: str,
    chunk_index: int,
    metadata: dict | None = None,
) -> DocumentChunkEntity:
    """Create a document chunk with a generated identifier."""
    return DocumentChunkEntity(
        chunk_id=generate_chunk_id(),
        document_id=document_id,
        content=content,
        chunk_index=chunk_index,
        metadata=metadata or {},
    )


def create_trend(
    title: str,
    region: str = "IN",
    timeframe: str = "now 7-d",
    trend_score: float | None = None,
    metadata: dict | None = None,
) -> TrendEntity:
    """Create a validated trend entity."""
    return TrendEntity(
        title=title,
        region=region,
        timeframe=timeframe,
        trend_score=trend_score,
        metadata=metadata or {},
    )


def create_news(
    title: str,
    url: str,
    source_name: str,
    **kwargs,
) -> NewsEntity:
    """Create a validated news entity."""
    return NewsEntity(
        title=title,
        url=url,
        source_name=source_name,
        **kwargs,
    )


def create_recommendation(
    title: str,
    description: str,
    rationale: str,
    content_format: ContentFormat,
    priority: RecommendationPriority = RecommendationPriority.MEDIUM,
    **kwargs,
) -> RecommendationEntity:
    """Create a validated recommendation entity."""
    return RecommendationEntity(
        title=title,
        description=description,
        rationale=rationale,
        content_format=content_format,
        priority=priority,
        **kwargs,
    )


def create_generated_content(
    recommendation_id: str,
    title: str,
    body: str,
    content_format: ContentFormat,
    language: str = "en",
) -> GeneratedContentEntity:
    """Create generated content linked to a recommendation."""
    return GeneratedContentEntity(
        content_id=generate_content_id(),
        recommendation_id=recommendation_id,
        title=title,
        body=body,
        content_format=content_format,
        language=language,
    )


__all__ = [
    "create_document",
    "create_document_chunk",
    "create_trend",
    "create_news",
    "create_recommendation",
    "create_generated_content",
]
