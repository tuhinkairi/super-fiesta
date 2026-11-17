"""
Centralized exception hierarchy for Context-Aware Suggestion RAG.

All custom exceptions inherit from ContextAwareSuggestionError,
allowing consuming applications to catch package-specific errors
using a single base exception.
"""


class ContextAwareSuggestionError(Exception):
    """Base exception for all package-specific errors."""


# ============================================================
# Configuration Exceptions
# ============================================================

class ConfigurationError(ContextAwareSuggestionError):
    """Raised when application configuration is invalid or incomplete."""


# ============================================================
# Document Ingestion Exceptions
# ============================================================

class DocumentError(ContextAwareSuggestionError):
    """Base exception for document-related failures."""


class DocumentValidationError(DocumentError):
    """Raised when a document fails validation."""


class DocumentLoadError(DocumentError):
    """Raised when a document cannot be loaded or parsed."""


class ChunkingError(DocumentError):
    """Raised when document chunking fails."""


# ============================================================
# Context Extraction Exceptions
# ============================================================

class ContextExtractionError(ContextAwareSuggestionError):
    """Raised when context cannot be extracted from documents."""


# ============================================================
# External Intelligence Exceptions
# ============================================================

class IntelligenceProviderError(ContextAwareSuggestionError):
    """Base exception for external intelligence provider failures."""


class TrendCollectionError(IntelligenceProviderError):
    """Raised when trend data collection or analysis fails."""


class NewsCollectionError(IntelligenceProviderError):
    """Raised when news collection or processing fails."""


# ============================================================
# Embedding Exceptions
# ============================================================

class EmbeddingError(ContextAwareSuggestionError):
    """Raised when dense or sparse embedding generation fails."""


# ============================================================
# Database Exceptions
# ============================================================

class DatabaseError(ContextAwareSuggestionError):
    """Base exception for database-related failures."""


class PineconeConnectionError(DatabaseError):
    """Raised when a connection to Pinecone fails."""


class IndexConfigurationError(DatabaseError):
    """Raised when Pinecone index configuration is invalid."""


# ============================================================
# Retrieval Exceptions
# ============================================================

class RetrievalError(ContextAwareSuggestionError):
    """Raised when document, trend, or news retrieval fails."""


# ============================================================
# Recommendation Exceptions
# ============================================================

class RecommendationError(ContextAwareSuggestionError):
    """Raised when recommendation scoring or ranking fails."""


# ============================================================
# LLM and Generation Exceptions
# ============================================================

class LLMError(ContextAwareSuggestionError):
    """Raised when an LLM request fails."""


class GenerationError(ContextAwareSuggestionError):
    """Raised when suggestion or content generation fails."""


class OutputValidationError(GenerationError):
    """Raised when generated output does not match the expected schema."""


# ============================================================
# Workflow Exceptions
# ============================================================

class WorkflowError(ContextAwareSuggestionError):
    """Raised when the LangGraph workflow fails."""


# ============================================================
# Security Exceptions
# ============================================================

class SecurityError(ContextAwareSuggestionError):
    """Raised when a security validation or policy check fails."""


__all__ = [
    "ContextAwareSuggestionError",
    "ConfigurationError",
    "DocumentError",
    "DocumentValidationError",
    "DocumentLoadError",
    "ChunkingError",
    "ContextExtractionError",
    "IntelligenceProviderError",
    "TrendCollectionError",
    "NewsCollectionError",
    "EmbeddingError",
    "DatabaseError",
    "PineconeConnectionError",
    "IndexConfigurationError",
    "RetrievalError",
    "RecommendationError",
    "LLMError",
    "GenerationError",
    "OutputValidationError",
    "WorkflowError",
    "SecurityError",
]
