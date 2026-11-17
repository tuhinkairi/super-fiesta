
"""
Context extraction utilities.

Provides lightweight rule-based extraction of topics, keywords,
and named entities from document text.

This module provides a baseline extractor that can later be
extended with NLP models and LLM-powered extraction.
"""

import re
from collections import Counter

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.context.models import (
    ExtractedContext,
    Keyword,
    NamedEntity,
    Topic,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.text import (
    normalize_text,
    validate_string,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.validators import validate_identifier


class RuleBasedContextExtractor:
    """Extract contextual information using text-processing rules."""

    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "been", "being",
        "by", "for", "from", "had", "has", "have", "he", "her",
        "his", "i", "in", "into", "is", "it", "its", "of", "on",
        "or", "our", "she", "that", "the", "their", "them", "there",
        "these", "they", "this", "those", "to", "was", "we", "were",
        "what", "when", "where", "which", "who", "will", "with",
        "you", "your", "about", "also", "can", "could", "does",
        "during", "each", "how", "if", "more", "most", "other",
        "such", "than", "then", "through", "very", "while",
    }

    DOMAIN_TERMS = {
        "artificial intelligence": [
            "artificial intelligence",
            "AI",
            "machine learning",
            "deep learning",
            "neural network",
        ],
        "cybersecurity": [
            "cybersecurity",
            "security",
            "encryption",
            "threat",
            "vulnerability",
            "malware",
        ],
        "retrieval augmented generation": [
            "retrieval augmented generation",
            "RAG",
            "retrieval",
            "embeddings",
            "vector database",
        ],
        "cloud computing": [
            "cloud computing",
            "cloud",
            "AWS",
            "Azure",
            "Google Cloud",
        ],
        "data science": [
            "data science",
            "data analysis",
            "statistics",
            "visualization",
        ],
        "software engineering": [
            "software engineering",
            "programming",
            "software development",
            "testing",
            "debugging",
        ],
    }

    EXCLUDED_ENTITIES = {
        "The", "This", "That", "These", "Those",
        "A", "An", "In", "On", "For", "With",
        "And", "But", "Or", "If", "When", "Where",
        "What", "Which", "Who", "How",
    }

    @staticmethod
    def _validate_limit(limit: int, field_name: str = "limit") -> None:
        """Validate an extraction result limit."""

        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError(f"{field_name} must be an integer")

        if limit < 1:
            raise ValueError(f"{field_name} must be at least 1")

    @staticmethod
    def _prepare_text(text: str) -> str:
        """Validate and normalize input text."""

        validate_string(text)
        normalized = normalize_text(text)

        if not normalized.strip():
            raise ValueError("Input text cannot be empty")

        return normalized

    def extract_keywords(
        self,
        text: str,
        limit: int = 20,
    ) -> list[Keyword]:
        """Extract frequently occurring words from text."""

        self._validate_limit(limit)
        text = self._prepare_text(text)

        words = re.findall(
            r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b",
            text.lower(),
        )

        filtered_words = [
            word
            for word in words
            if word not in self.STOP_WORDS and len(word) > 2
        ]

        counts = Counter(filtered_words)
        total = sum(counts.values()) or 1

        return [
            Keyword(
                text=word,
                frequency=count,
                relevance_score=min(count / total * 10, 1.0),
                is_phrase=False,
            )
            for word, count in counts.most_common(limit)
        ]

    def extract_topics(
        self,
        text: str,
        limit: int = 10,
    ) -> list[Topic]:
        """Identify topics using predefined domain-term matching."""

        self._validate_limit(limit)
        text_lower = self._prepare_text(text).lower()

        topics: list[Topic] = []

        for topic_name, related_terms in self.DOMAIN_TERMS.items():
            matched_terms = [
                term
                for term in related_terms
                if term.lower() in text_lower
            ]

            if matched_terms:
                score = min(
                    0.5 + (len(matched_terms) * 0.1),
                    1.0,
                )

                topics.append(
                    Topic(
                        name=topic_name.title(),
                        relevance_score=score,
                        keywords=matched_terms,
                    )
                )

        topics.sort(
            key=lambda topic: topic.relevance_score,
            reverse=True,
        )

        return topics[:limit]

    def extract_entities(
        self,
        text: str,
        limit: int = 30,
    ) -> list[NamedEntity]:
        """
        Identify possible named entities using capitalization.

        This is a heuristic, not a full named-entity recognition model.
        """

        self._validate_limit(limit)
        text = self._prepare_text(text)

        pattern = (
            r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*\b"
        )

        matches = re.findall(pattern, text)

        counts = Counter(
            match.strip()
            for match in matches
            if match.strip() not in self.EXCLUDED_ENTITIES
        )

        return [
            NamedEntity(
                text=entity,
                entity_type="UNKNOWN",
                relevance_score=min(0.5 + count * 0.1, 1.0),
                occurrences=count,
            )
            for entity, count in counts.most_common(limit)
        ]

    def extract(
        self,
        text: str,
        document_id: str,
        language: str = "en",
        region: str = "IN",
    ) -> ExtractedContext:
        """Extract topics, keywords, and entities from a document."""

        text = self._prepare_text(text)
        validate_identifier(document_id, field_name="document_id")

        if not language.strip():
            raise ValueError("language cannot be empty")

        if not region.strip():
            raise ValueError("region cannot be empty")

        return ExtractedContext(
            document_id=document_id,
            topics=self.extract_topics(text),
            keywords=self.extract_keywords(text),
            entities=self.extract_entities(text),
            language=language,
            region=region,
            extraction_method="rule_based",
        )


_default_extractor = RuleBasedContextExtractor()


def extract_context(
    text: str,
    document_id: str,
    language: str = "en",
    region: str = "IN",
) -> ExtractedContext:
    """Convenience function for extracting document context."""

    return _default_extractor.extract(
        text=text,
        document_id=document_id,
        language=language,
        region=region,
    )


__all__ = [
    "RuleBasedContextExtractor",
    "extract_context",
]
