"""
Document summarization utilities.

Provides extractive summarization by selecting important sentences
from the original document.

This implementation does not require an external LLM.
"""

import re
from collections import Counter

from context_aware_suggestion_rag.context.models import DocumentSummary
from context_aware_suggestion_rag.core.text import (
    normalize_text,
    validate_string,
)
from context_aware_suggestion_rag.core.validators import validate_identifier


class ExtractiveSummarizer:
    """Generate summaries by ranking and selecting document sentences."""

    STOP_WORDS = {
        "a", "an", "and", "are", "as", "at", "be", "been", "being",
        "by", "for", "from", "had", "has", "have", "he", "her",
        "his", "i", "in", "into", "is", "it", "its", "of", "on",
        "or", "our", "she", "that", "the", "their", "them", "there",
        "these", "they", "this", "those", "to", "was", "we", "were",
        "what", "when", "where", "which", "who", "will", "with",
        "you", "your", "about", "also", "can", "could", "during",
        "each", "how", "if", "more", "most", "other", "such",
        "than", "then", "through", "very", "while",
    }

    def __init__(self, max_sentences: int = 5) -> None:
        if isinstance(max_sentences, bool) or not isinstance(max_sentences, int):
            raise TypeError("max_sentences must be an integer")

        if max_sentences < 1:
            raise ValueError("max_sentences must be at least 1")

        self.max_sentences = max_sentences

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split text into individual sentences."""

        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            text,
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def _score_sentences(self, sentences: list[str]) -> list[tuple[int, float]]:
        """Calculate importance scores for sentences."""

        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b", " ".join(sentences).lower())

        filtered_words = [
            word for word in words
            if word not in self.STOP_WORDS and len(word) > 2
        ]

        frequencies = Counter(filtered_words)
        maximum_frequency = max(frequencies.values(), default=1)

        scored_sentences: list[tuple[int, float]] = []

        for index, sentence in enumerate(sentences):
            sentence_words = re.findall(
                r"\b[a-zA-Z][a-zA-Z0-9+#.-]*\b",
                sentence.lower(),
            )

            meaningful_words = [
                word for word in sentence_words
                if word not in self.STOP_WORDS and len(word) > 2
            ]

            if not meaningful_words:
                score = 0.0
            else:
                score = sum(
                    frequencies[word] / maximum_frequency
                    for word in meaningful_words
                ) / len(meaningful_words)

            # Give a small preference to earlier sentences.
            position_bonus = 1.0 / (index + 1)
            score += position_bonus * 0.1

            scored_sentences.append((index, score))

        return scored_sentences

    def summarize(
        self,
        text: str,
        max_sentences: int | None = None,
    ) -> str:
        """Generate an extractive summary from document text."""

        validate_string(text)
        normalized_text = normalize_text(text)

        if not normalized_text.strip():
            raise ValueError("Document text cannot be empty")

        sentence_limit = (
            max_sentences
            if max_sentences is not None
            else self.max_sentences
        )

        if isinstance(sentence_limit, bool) or not isinstance(sentence_limit, int):
            raise TypeError("max_sentences must be an integer")

        if sentence_limit < 1:
            raise ValueError("max_sentences must be at least 1")

        sentences = self._split_sentences(normalized_text)

        if len(sentences) <= sentence_limit:
            return " ".join(sentences)

        scored_sentences = self._score_sentences(sentences)

        selected = sorted(
            scored_sentences,
            key=lambda item: item[1],
            reverse=True,
        )[:sentence_limit]

        selected_indices = sorted(index for index, _ in selected)

        return " ".join(sentences[index] for index in selected_indices)

    def summarize_to_model(
        self,
        text: str,
        document_id: str,
        title: str = "",
        max_sentences: int | None = None,
    ) -> DocumentSummary:
        """Generate a structured document summary."""

        validate_identifier(document_id, field_name="document_id")

        summary_text = self.summarize(
            text=text,
            max_sentences=max_sentences,
        )

        key_points = self._split_sentences(summary_text)

        return DocumentSummary(
            document_id=document_id,
            title=title,
            summary=summary_text,
            key_points=key_points,
            word_count=len(summary_text.split()),
        )


_default_summarizer = ExtractiveSummarizer()


def summarize_document(
    text: str,
    document_id: str,
    title: str = "",
    max_sentences: int = 5,
) -> DocumentSummary:
    """Convenience function for summarizing a document."""

    return _default_summarizer.summarize_to_model(
        text=text,
        document_id=document_id,
        title=title,
        max_sentences=max_sentences,
    )


__all__ = [
    "ExtractiveSummarizer",
    "summarize_document",
]
