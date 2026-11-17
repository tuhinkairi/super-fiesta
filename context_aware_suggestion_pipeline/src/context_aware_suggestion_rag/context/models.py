"""
Context extraction models.

Defines standardized models for topics, keywords, entities,
document summaries, and extracted document context.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import Field

from context_aware_suggestion_rag.domain.entities import DomainEntity


def current_utc_time() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


class ContextModel(DomainEntity):
    """Base model for context extraction data."""

    pass


class Topic(ContextModel):
    """Represents an identified topic or subject."""

    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=1000)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    keywords: list[str] = Field(default_factory=list)
    subtopics: list[str] = Field(default_factory=list)


class Keyword(ContextModel):
    """Represents an important keyword or key phrase."""

    text: str = Field(min_length=1, max_length=200)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    frequency: int = Field(default=1, ge=1)
    is_phrase: bool = False


class NamedEntity(ContextModel):
    """Represents a named entity extracted from document text."""

    text: str = Field(min_length=1, max_length=300)
    entity_type: str = Field(min_length=1, max_length=100)
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    occurrences: int = Field(default=1, ge=1)


class DocumentSummary(ContextModel):
    """Represents a generated summary of a document."""

    document_id: str = Field(min_length=1)
    title: str = Field(default="", max_length=300)
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    word_count: int = Field(default=0, ge=0)
    generated_at: datetime = Field(default_factory=current_utc_time)


class ExtractedContext(ContextModel):
    """Contains all extracted contextual information for a document."""

    document_id: str = Field(min_length=1)

    topics: list[Topic] = Field(default_factory=list)
    keywords: list[Keyword] = Field(default_factory=list)
    entities: list[NamedEntity] = Field(default_factory=list)

    summary: DocumentSummary | None = None

    language: str = "en"
    region: str = "IN"

    extraction_method: str = "hybrid"
    extraction_time_seconds: float = Field(default=0.0, ge=0.0)

    extracted_at: datetime = Field(default_factory=current_utc_time)

    metadata: dict[str, Any] = Field(default_factory=dict)


__all__ = [
    "ContextModel",
    "Topic",
    "Keyword",
    "NamedEntity",
    "DocumentSummary",
    "ExtractedContext",
    "current_utc_time",
]
