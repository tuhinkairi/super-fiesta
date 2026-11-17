"""
Context processing service.

Coordinates context extraction, summarization, analysis,
and merging operations.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.analyzers import (
    ContextAnalysis,
    ContextAnalyzer,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.extractors import (
    RuleBasedContextExtractor,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.mergers import ContextMerger
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import ExtractedContext
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.summarizers import (
    ExtractiveSummarizer,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.validators import validate_identifier


class ContextService:
    """Coordinate all document context-processing operations."""

    def __init__(
        self,
        extractor: RuleBasedContextExtractor | None = None,
        summarizer: ExtractiveSummarizer | None = None,
        analyzer: ContextAnalyzer | None = None,
        merger: ContextMerger | None = None,
    ) -> None:
        self.extractor = extractor or RuleBasedContextExtractor()
        self.summarizer = summarizer or ExtractiveSummarizer()
        self.analyzer = analyzer or ContextAnalyzer()
        self.merger = merger or ContextMerger()

    def extract_context(
        self,
        text: str,
        document_id: str,
        language: str = "en",
        region: str = "IN",
    ) -> ExtractedContext:
        """Extract topics, keywords, and entities from document text."""

        return self.extractor.extract(
            text=text,
            document_id=document_id,
            language=language,
            region=region,
        )

    def summarize_document(
        self,
        text: str,
        document_id: str,
        title: str = "",
        max_sentences: int | None = None,
    ):
        """Generate a structured document summary."""

        validate_identifier(document_id, field_name="document_id")

        return self.summarizer.summarize_to_model(
            text=text,
            document_id=document_id,
            title=title,
            max_sentences=max_sentences,
        )

    def analyze_context(
        self,
        context: ExtractedContext,
    ) -> ContextAnalysis:
        """Analyze extracted contextual information."""

        return self.analyzer.analyze(context)

    def merge_contexts(
        self,
        contexts: list[ExtractedContext],
        merged_document_id: str = "merged_context",
    ) -> ExtractedContext:
        """Merge contextual information from multiple documents."""

        return self.merger.merge(
            contexts=contexts,
            merged_document_id=merged_document_id,
        )

    def process_document(
        self,
        text: str,
        document_id: str,
        title: str = "",
        language: str = "en",
        region: str = "IN",
        generate_summary: bool = True,
    ) -> tuple[ExtractedContext, ContextAnalysis]:
        """
        Extract and analyze all available context from a document.

        Optionally generates a summary before returning the results.
        """

        context = self.extract_context(
            text=text,
            document_id=document_id,
            language=language,
            region=region,
        )

        if generate_summary:
            context.summary = self.summarize_document(
                text=text,
                document_id=document_id,
                title=title,
            )

        analysis = self.analyze_context(context)

        return context, analysis


_default_context_service = ContextService()


def process_document_context(
    text: str,
    document_id: str,
    title: str = "",
    language: str = "en",
    region: str = "IN",
) -> tuple[ExtractedContext, ContextAnalysis]:
    """Convenience function for complete context processing."""

    return _default_context_service.process_document(
        text=text,
        document_id=document_id,
        title=title,
        language=language,
        region=region,
    )


__all__ = [
    "ContextService",
    "process_document_context",
]
