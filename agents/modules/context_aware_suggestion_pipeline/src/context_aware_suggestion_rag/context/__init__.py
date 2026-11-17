"""
Context extraction, analysis, summarization, and merging package.

Provides a unified public interface for processing document context.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import (
    ContextModel,
    Topic,
    Keyword,
    NamedEntity,
    DocumentSummary,
    ExtractedContext,
    current_utc_time,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.extractors import (
    RuleBasedContextExtractor,
    extract_context,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.summarizers import (
    ExtractiveSummarizer,
    summarize_document,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.analyzers import (
    ContextAnalysis,
    ContextAnalyzer,
    analyze_context,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.mergers import (
    ContextMerger,
    merge_contexts,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.service import (
    ContextService,
    process_document_context,
)


__all__ = [
    # Models
    "ContextModel",
    "Topic",
    "Keyword",
    "NamedEntity",
    "DocumentSummary",
    "ExtractedContext",
    "current_utc_time",

    # Extraction
    "RuleBasedContextExtractor",
    "extract_context",

    # Summarization
    "ExtractiveSummarizer",
    "summarize_document",

    # Analysis
    "ContextAnalysis",
    "ContextAnalyzer",
    "analyze_context",

    # Merging
    "ContextMerger",
    "merge_contexts",

    # Service
    "ContextService",
    "process_document_context",
]
