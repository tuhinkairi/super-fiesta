"""
Context analysis utilities.

Analyzes extracted topics, keywords, entities, and summaries
to generate measurable insights about document context.
"""

from collections import Counter
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from context_aware_suggestion_rag.context.models import ExtractedContext


class ContextAnalysis(BaseModel):
    """Structured analysis report for extracted document context."""

    model_config = ConfigDict(extra="forbid")

    document_id: str

    total_topics: int = Field(default=0, ge=0)
    total_keywords: int = Field(default=0, ge=0)
    total_entities: int = Field(default=0, ge=0)

    top_topics: list[str] = Field(default_factory=list)
    top_keywords: list[str] = Field(default_factory=list)
    frequent_entities: list[str] = Field(default_factory=list)

    topic_diversity_score: float = Field(default=0.0, ge=0.0, le=1.0)
    context_completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)

    dominant_topic: str | None = None

    insights: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    analysis_metadata: dict[str, Any] = Field(default_factory=dict)


class ContextAnalyzer:
    """Analyze the quality and characteristics of extracted context."""

    def analyze_topics(
        self,
        context: ExtractedContext,
    ) -> tuple[list[str], str | None, float]:
        """Analyze topic distribution and diversity."""

        topics = context.topics

        if not topics:
            return [], None, 0.0

        sorted_topics = sorted(
            topics,
            key=lambda topic: topic.relevance_score,
            reverse=True,
        )

        topic_names = [topic.name for topic in sorted_topics]

        dominant_topic = topic_names[0]

        diversity_score = min(len(set(topic_names)) / 5, 1.0)

        return topic_names, dominant_topic, diversity_score

    def analyze_keywords(
        self,
        context: ExtractedContext,
        limit: int = 10,
    ) -> list[str]:
        """Return the most relevant keywords."""

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        sorted_keywords = sorted(
            context.keywords,
            key=lambda keyword: (
                keyword.relevance_score,
                keyword.frequency,
            ),
            reverse=True,
        )

        return [
            keyword.text
            for keyword in sorted_keywords[:limit]
        ]

    def analyze_entities(
        self,
        context: ExtractedContext,
        limit: int = 10,
    ) -> list[str]:
        """Return the most frequently occurring entities."""

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        entity_counts = Counter()

        for entity in context.entities:
            entity_counts[entity.text] += entity.occurrences

        return [
            entity
            for entity, _ in entity_counts.most_common(limit)
        ]

    @staticmethod
    def calculate_completeness(
        context: ExtractedContext,
    ) -> float:
        """Estimate how much contextual information was extracted."""

        components = [
            bool(context.topics),
            bool(context.keywords),
            bool(context.entities),
            context.summary is not None,
        ]

        return sum(components) / len(components)

    def generate_insights(
        self,
        context: ExtractedContext,
    ) -> tuple[list[str], list[str]]:
        """Generate simple insights and warnings."""

        insights: list[str] = []
        warnings: list[str] = []

        if context.topics:
            insights.append(
                f"Identified {len(context.topics)} topic(s) in the document."
            )
        else:
            warnings.append("No topics were identified.")

        if context.keywords:
            insights.append(
                f"Extracted {len(context.keywords)} keyword(s)."
            )
        else:
            warnings.append("No keywords were extracted.")

        if context.entities:
            insights.append(
                f"Identified {len(context.entities)} named entity occurrence record(s)."
            )
        else:
            warnings.append("No named entities were identified.")

        if context.summary:
            insights.append("A document summary is available.")
        else:
            warnings.append("The document has not been summarized.")

        completeness = self.calculate_completeness(context)

        if completeness < 0.5:
            warnings.append("Context extraction is incomplete.")

        return insights, warnings

    def analyze(
        self,
        context: ExtractedContext,
        keyword_limit: int = 10,
        entity_limit: int = 10,
    ) -> ContextAnalysis:
        """Generate a complete context analysis report."""

        if not isinstance(context, ExtractedContext):
            raise TypeError("context must be an ExtractedContext instance")

        topics, dominant_topic, diversity = self.analyze_topics(context)

        keywords = self.analyze_keywords(
            context,
            limit=keyword_limit,
        )

        entities = self.analyze_entities(
            context,
            limit=entity_limit,
        )

        completeness = self.calculate_completeness(context)

        insights, warnings = self.generate_insights(context)

        return ContextAnalysis(
            document_id=context.document_id,
            total_topics=len(context.topics),
            total_keywords=len(context.keywords),
            total_entities=len(context.entities),
            top_topics=topics[:keyword_limit],
            top_keywords=keywords,
            frequent_entities=entities,
            topic_diversity_score=diversity,
            context_completeness_score=completeness,
            dominant_topic=dominant_topic,
            insights=insights,
            warnings=warnings,
            analysis_metadata={
                "language": context.language,
                "region": context.region,
                "extraction_method": context.extraction_method,
            },
        )


_default_analyzer = ContextAnalyzer()


def analyze_context(
    context: ExtractedContext,
) -> ContextAnalysis:
    """Convenience function for analyzing extracted context."""

    return _default_analyzer.analyze(context)


__all__ = [
    "ContextAnalysis",
    "ContextAnalyzer",
    "analyze_context",
]
