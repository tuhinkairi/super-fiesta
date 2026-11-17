"""
Domain schemas.

Defines validated request and response schemas for document
ingestion, context-aware queries, recommendations, and pipeline
execution.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.domain.enums import (
    ContentFormat,
    RecommendationPriority,
)


class DomainSchema(BaseModel):
    """Base configuration shared by domain schemas."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class DocumentIngestionRequest(DomainSchema):
    """Request schema for ingesting a document."""

    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)
    language: str = Field(default="en", min_length=2, max_length=12)
    region: str = Field(default="IN", min_length=2, max_length=3)
    metadata: dict[str, str | int | float | bool | list[str]] = Field(
        default_factory=dict
    )


class DocumentIngestionResponse(DomainSchema):
    """Response returned after document ingestion."""

    document_id: str
    filename: str
    status: str
    total_chunks: int = Field(ge=0)
    message: str
    created_at: datetime


class SuggestionRequest(DomainSchema):
    """User request for context-aware content suggestions."""

    query: str = Field(min_length=1, max_length=10_000)
    document_ids: list[str] = Field(default_factory=list)
    language: str = Field(default="en", min_length=2, max_length=12)
    region: str = Field(default="IN", min_length=2, max_length=3)
    content_formats: list[ContentFormat] = Field(
        default_factory=lambda: [ContentFormat.BLOG_POST]
    )
    max_recommendations: int = Field(default=5, ge=1, le=50)
    include_trends: bool = True
    include_news: bool = True
    generate_content: bool = False


class RecommendationResponse(DomainSchema):
    """Structured recommendation returned to the caller."""

    recommendation_id: str
    title: str
    description: str
    rationale: str
    source_ids: list[str] = Field(default_factory=list)
    content_format: ContentFormat
    priority: RecommendationPriority
    confidence: float | None = Field(default=None, ge=0, le=1)


class GeneratedContentResponse(DomainSchema):
    """Structured generated content returned to the caller."""

    content_id: str
    recommendation_id: str
    title: str
    body: str
    content_format: ContentFormat
    language: str = "en"
    created_at: datetime


class PipelineResponse(DomainSchema):
    """Final response schema for a pipeline execution."""

    request_id: str
    recommendations: list[RecommendationResponse] = Field(
        default_factory=list
    )
    generated_content: list[GeneratedContentResponse] = Field(
        default_factory=list
    )
    retrieved_context: list[dict[str, str | int | float | bool]] = Field(
        default_factory=list
    )
    execution_time_seconds: float = Field(default=0.0, ge=0)
    created_at: datetime


class NewsSourceSchema(DomainSchema):
    """Represents a validated external news source."""

    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    source_name: str = Field(min_length=1, max_length=200)
    published_at: datetime | None = None
    summary: str = Field(default="", max_length=10_000)


__all__ = [
    "DomainSchema",
    "DocumentIngestionRequest",
    "DocumentIngestionResponse",
    "SuggestionRequest",
    "RecommendationResponse",
    "GeneratedContentResponse",
    "PipelineResponse",
    "NewsSourceSchema",
]
