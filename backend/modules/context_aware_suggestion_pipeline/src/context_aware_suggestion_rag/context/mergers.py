"""
Context merging utilities.

Combines extracted context from multiple documents into
a unified context profile.
"""

from collections import Counter

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import (
    DocumentSummary,
    ExtractedContext,
    Keyword,
    NamedEntity,
    Topic,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.validators import validate_identifier


class ContextMerger:
    """Merge contextual information from multiple documents."""

    def merge_topics(
        self,
        contexts: list[ExtractedContext],
    ) -> list[Topic]:
        """Merge topics and combine their relevance scores."""

        merged: dict[str, Topic] = {}

        for context in contexts:
            for topic in context.topics:
                key = topic.name.casefold()

                if key not in merged:
                    merged[key] = topic.model_copy(
                        deep=True,
                        update={
                            "keywords": list(topic.keywords),
                            "subtopics": list(topic.subtopics),
                        },
                    )
                    continue

                existing = merged[key]

                existing.relevance_score = max(
                    existing.relevance_score,
                    topic.relevance_score,
                )

                existing.keywords = list(
                    dict.fromkeys(existing.keywords + topic.keywords)
                )

                existing.subtopics = list(
                    dict.fromkeys(existing.subtopics + topic.subtopics)
                )

                if not existing.description and topic.description:
                    existing.description = topic.description

        return sorted(
            merged.values(),
            key=lambda topic: topic.relevance_score,
            reverse=True,
        )

    def merge_keywords(
        self,
        contexts: list[ExtractedContext],
    ) -> list[Keyword]:
        """Merge duplicate keywords and aggregate their frequencies."""

        merged: dict[str, Keyword] = {}

        for context in contexts:
            for keyword in context.keywords:
                key = keyword.text.casefold()

                if key not in merged:
                    merged[key] = keyword.model_copy(deep=True)
                    continue

                existing = merged[key]

                existing.frequency += keyword.frequency

                existing.relevance_score = max(
                    existing.relevance_score,
                    keyword.relevance_score,
                )

                existing.is_phrase = (
                    existing.is_phrase or keyword.is_phrase
                )

        return sorted(
            merged.values(),
            key=lambda keyword: (
                keyword.relevance_score,
                keyword.frequency,
            ),
            reverse=True,
        )

    def merge_entities(
        self,
        contexts: list[ExtractedContext],
    ) -> list[NamedEntity]:
        """Merge duplicate entities and aggregate occurrences."""

        merged: dict[tuple[str, str], NamedEntity] = {}

        for context in contexts:
            for entity in context.entities:
                key = (
                    entity.text.casefold(),
                    entity.entity_type.casefold(),
                )

                if key not in merged:
                    merged[key] = entity.model_copy(deep=True)
                    continue

                existing = merged[key]

                existing.occurrences += entity.occurrences

                existing.relevance_score = max(
                    existing.relevance_score,
                    entity.relevance_score,
                )

        return sorted(
            merged.values(),
            key=lambda entity: (
                entity.relevance_score,
                entity.occurrences,
            ),
            reverse=True,
        )

    @staticmethod
    def merge_summaries(
        contexts: list[ExtractedContext],
    ) -> list[DocumentSummary]:
        """Collect available document summaries."""

        summaries: list[DocumentSummary] = []

        for context in contexts:
            if context.summary is not None:
                summaries.append(context.summary)

        return summaries

    def merge(
        self,
        contexts: list[ExtractedContext],
        merged_document_id: str = "merged_context",
    ) -> ExtractedContext:
        """Merge multiple extracted contexts into one context."""

        if not contexts:
            raise ValueError("At least one context is required")

        for context in contexts:
            if not isinstance(context, ExtractedContext):
                raise TypeError(
                    "Every item must be an ExtractedContext instance"
                )

        validate_identifier(
            merged_document_id,
            field_name="merged_document_id",
        )

        topics = self.merge_topics(contexts)
        keywords = self.merge_keywords(contexts)
        entities = self.merge_entities(contexts)
        summaries = self.merge_summaries(contexts)

        summary_text = "\n\n".join(
            f"{summary.title or summary.document_id}: {summary.summary}"
            for summary in summaries
        )

        merged_summary = None

        if summary_text:
            merged_summary = DocumentSummary(
                document_id=merged_document_id,
                title="Combined Document Summary",
                summary=summary_text,
                key_points=[
                    point
                    for summary in summaries
                    for point in summary.key_points
                ],
                word_count=len(summary_text.split()),
            )

        languages = Counter(
            context.language for context in contexts
        )

        regions = Counter(
            context.region for context in contexts
        )

        extraction_methods = sorted(
            {
                context.extraction_method
                for context in contexts
            }
        )

        return ExtractedContext(
            document_id=merged_document_id,
            topics=topics,
            keywords=keywords,
            entities=entities,
            summary=merged_summary,
            language=languages.most_common(1)[0][0],
            region=regions.most_common(1)[0][0],
            extraction_method="merged:" + ",".join(extraction_methods),
            metadata={
                "merged_document_count": len(contexts),
                "source_document_ids": [
                    context.document_id for context in contexts
                ],
                "source_summary_count": len(summaries),
            },
        )


_default_merger = ContextMerger()


def merge_contexts(
    contexts: list[ExtractedContext],
    merged_document_id: str = "merged_context",
) -> ExtractedContext:
    """Convenience function for merging multiple contexts."""

    return _default_merger.merge(
        contexts=contexts,
        merged_document_id=merged_document_id,
    )


__all__ = [
    "ContextMerger",
    "merge_contexts",
]
