"""Integration between extracted document context and external intelligence."""

from __future__ import annotations

from dataclasses import dataclass

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import ExtractedContext
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.models import (
    IntelligenceCollectionResult,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.intelligence.service import (
    IntelligenceService,
)


@dataclass(slots=True)
class ContextIntelligenceResult:
    """Combined document context and external intelligence."""

    context: ExtractedContext
    intelligence: IntelligenceCollectionResult
    search_query: str | None


class ContextIntelligenceProcessor:
    """Collect trends and news using extracted document context."""

    def __init__(
        self,
        intelligence_service: IntelligenceService | None = None,
        max_query_terms: int = 12,
    ) -> None:
        if (
            isinstance(max_query_terms, bool)
            or not isinstance(max_query_terms, int)
            or max_query_terms < 1
        ):
            raise ValueError("max_query_terms must be a positive integer")

        self.intelligence_service = (
            intelligence_service
            if intelligence_service is not None
            else IntelligenceService()
        )

        self.max_query_terms = max_query_terms

    def build_search_query(
        self,
        context: ExtractedContext,
    ) -> str | None:
        """Build a focused search query from extracted context."""

        terms: list[str] = []
        seen: set[str] = set()

        candidates = (
            [topic.name for topic in context.topics]
            + [keyword.text for keyword in context.keywords]
            + [entity.text for entity in context.entities]
        )

        for candidate in candidates:
            term = candidate.strip()

            if not term:
                continue

            normalized = term.casefold()

            if normalized in seen:
                continue

            seen.add(normalized)
            terms.append(term)

            if len(terms) >= self.max_query_terms:
                break

        return " ".join(terms) if terms else None

    def collect_for_context(
        self,
        context: ExtractedContext,
        trend_limit: int = 20,
        news_limit: int = 30,
    ) -> ContextIntelligenceResult:
        """Collect external intelligence relevant to document context."""

        if not isinstance(context, ExtractedContext):
            raise TypeError("context must be an ExtractedContext instance")

        query = self.build_search_query(context)

        intelligence = self.intelligence_service.collect(
            region=context.region,
            language=context.language,
            query=query,
            trend_limit=trend_limit,
            news_limit=news_limit,
        )

        return ContextIntelligenceResult(
            context=context,
            intelligence=intelligence,
            search_query=query,
        )

    def close(self) -> None:
        """Close the underlying intelligence service."""

        self.intelligence_service.close()


__all__ = [
    "ContextIntelligenceResult",
    "ContextIntelligenceProcessor",
]
