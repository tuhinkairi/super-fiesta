"""
Domain enumerations.

Defines standardized values for document types, data sources,
content formats, recommendation priorities, and workflow states.
"""

from enum import StrEnum


class DocumentType(StrEnum):
    """Supported document formats."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    JSON = "json"


class SourceType(StrEnum):
    """Types of information sources used by the pipeline."""

    DOCUMENT = "document"
    TREND = "trend"
    NEWS = "news"


class ContentFormat(StrEnum):
    """Supported content formats for recommendations."""

    BLOG_POST = "blog_post"
    LINKEDIN_POST = "linkedin_post"
    INSTAGRAM_POST = "instagram_post"
    X_POST = "x_post"
    NEWSLETTER = "newsletter"
    VIDEO_SCRIPT = "video_script"
    INFOGRAPHIC = "infographic"
    ARTICLE = "article"


class RecommendationPriority(StrEnum):
    """Priority levels assigned to recommendations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkflowStatus(StrEnum):
    """Execution states of the RAG workflow."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingStatus(StrEnum):
    """Processing states for individual documents and records."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


__all__ = [
    "DocumentType",
    "SourceType",
    "ContentFormat",
    "RecommendationPriority",
    "WorkflowStatus",
    "ProcessingStatus",
]
