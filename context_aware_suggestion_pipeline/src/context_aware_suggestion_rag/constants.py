"""
Shared constants for the Context-Aware Suggestion RAG package.

This module contains package-wide identifiers and fixed values.

Runtime-configurable values belong in the config package instead.
"""

from typing import Final


# ============================================================
# Package Information
# ============================================================

PACKAGE_NAME: Final[str] = "context_aware_suggestion_rag"


# ============================================================
# Pinecone Namespace Identifiers
# ============================================================

# Documents uploaded by users or external pipelines.
DOCUMENT_NAMESPACE: Final[str] = "documents"

# Trending topics and search trend information.
TREND_NAMESPACE: Final[str] = "trends"

# News articles and current events.
NEWS_NAMESPACE: Final[str] = "news"


# ============================================================
# Supported Document Extensions
# ============================================================

SUPPORTED_DOCUMENT_EXTENSIONS: Final[frozenset[str]] = frozenset(
    {
        ".pdf",
        ".docx",
        ".txt",
        ".json",
    }
)


# ============================================================
# Content Source Identifiers
# ============================================================

SOURCE_DOCUMENT: Final[str] = "document"
SOURCE_TREND: Final[str] = "trend"
SOURCE_NEWS: Final[str] = "news"


# ============================================================
# Standard Metadata Field Names
# ============================================================

# General metadata
METADATA_ID: Final[str] = "id"
METADATA_SOURCE: Final[str] = "source"
METADATA_SOURCE_TYPE: Final[str] = "source_type"
METADATA_CREATED_AT: Final[str] = "created_at"
METADATA_UPDATED_AT: Final[str] = "updated_at"
METADATA_EXPIRES_AT: Final[str] = "expires_at"

# Document metadata
METADATA_DOCUMENT_ID: Final[str] = "document_id"
METADATA_CHUNK_ID: Final[str] = "chunk_id"
METADATA_DOCUMENT_NAME: Final[str] = "document_name"
METADATA_DOCUMENT_TYPE: Final[str] = "document_type"

# Content metadata
METADATA_TITLE: Final[str] = "title"
METADATA_CONTENT: Final[str] = "content"
METADATA_TOPIC: Final[str] = "topic"
METADATA_KEYWORDS: Final[str] = "keywords"
METADATA_LANGUAGE: Final[str] = "language"
METADATA_REGION: Final[str] = "region"

# Intelligence metadata
METADATA_TREND_SCORE: Final[str] = "trend_score"
METADATA_NEWS_CATEGORY: Final[str] = "news_category"
METADATA_PUBLISHED_AT: Final[str] = "published_at"
METADATA_URL: Final[str] = "url"


# ============================================================
# Default Text Values
# ============================================================

DEFAULT_LANGUAGE: Final[str] = "en"
DEFAULT_REGION: Final[str] = "IN"


__all__ = [
    "PACKAGE_NAME",
    "DOCUMENT_NAMESPACE",
    "TREND_NAMESPACE",
    "NEWS_NAMESPACE",
    "SUPPORTED_DOCUMENT_EXTENSIONS",
    "SOURCE_DOCUMENT",
    "SOURCE_TREND",
    "SOURCE_NEWS",
    "METADATA_ID",
    "METADATA_SOURCE",
    "METADATA_SOURCE_TYPE",
    "METADATA_CREATED_AT",
    "METADATA_UPDATED_AT",
    "METADATA_EXPIRES_AT",
    "METADATA_DOCUMENT_ID",
    "METADATA_CHUNK_ID",
    "METADATA_DOCUMENT_NAME",
    "METADATA_DOCUMENT_TYPE",
    "METADATA_TITLE",
    "METADATA_CONTENT",
    "METADATA_TOPIC",
    "METADATA_KEYWORDS",
    "METADATA_LANGUAGE",
    "METADATA_REGION",
    "METADATA_TREND_SCORE",
    "METADATA_NEWS_CATEGORY",
    "METADATA_PUBLISHED_AT",
    "METADATA_URL",
    "DEFAULT_LANGUAGE",
    "DEFAULT_REGION",
]
