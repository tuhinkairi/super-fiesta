"""
Validation utilities for generated content.

Checks generated content, metadata, word counts, required phrases,
prohibited phrases, and generation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
    GenerationResult,
    GenerationStatus,
)


@dataclass(frozen=True, slots=True)
class ContentValidationConfig:
    """Configurable rules for generated-content validation."""

    min_word_count: int = 1
    max_word_count: int = 10000
    required_phrases: tuple[str, ...] = ()
    prohibited_phrases: tuple[str, ...] = ()
    allow_empty_title: bool = True
    allow_empty_description: bool = True

    def __post_init__(self) -> None:
        if (
            isinstance(self.min_word_count, bool)
            or not isinstance(self.min_word_count, int)
            or self.min_word_count < 0
        ):
            raise ValueError(
                "min_word_count must be a non-negative integer."
            )

        if (
            isinstance(self.max_word_count, bool)
            or not isinstance(self.max_word_count, int)
            or self.max_word_count <= 0
        ):
            raise ValueError(
                "max_word_count must be a positive integer."
            )

        if self.min_word_count > self.max_word_count:
            raise ValueError(
                "min_word_count cannot exceed max_word_count."
            )

        for field_name, phrases in (
            ("required_phrases", self.required_phrases),
            ("prohibited_phrases", self.prohibited_phrases),
        ):
            if not isinstance(phrases, tuple):
                raise TypeError(f"{field_name} must be a tuple.")

            if any(
                not isinstance(phrase, str) or not phrase.strip()
                for phrase in phrases
            ):
                raise ValueError(
                    f"Every phrase in {field_name} must be non-empty."
                )

        if not isinstance(self.allow_empty_title, bool):
            raise TypeError("allow_empty_title must be a boolean.")

        if not isinstance(self.allow_empty_description, bool):
            raise TypeError(
                "allow_empty_description must be a boolean."
            )


@dataclass(slots=True)
class ContentValidationResult:
    """Contains validation outcome and associated issues."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.is_valid, bool):
            raise TypeError("is_valid must be a boolean.")

        if not isinstance(self.errors, list):
            raise TypeError("errors must be a list.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")

        if any(not isinstance(item, str) for item in self.errors):
            raise TypeError("Every error must be a string.")

        if any(not isinstance(item, str) for item in self.warnings):
            raise TypeError("Every warning must be a string.")

        if self.is_valid and self.errors:
            raise ValueError(
                "A valid result cannot contain validation errors."
            )


class GeneratedContentValidator:
    """Validates generated content and generation results."""

    def __init__(
        self,
        config: ContentValidationConfig | None = None,
    ) -> None:
        self.config = config or ContentValidationConfig()

    def validate(
        self,
        content: GeneratedContent,
    ) -> ContentValidationResult:
        """Validate a generated-content object."""

        if not isinstance(content, GeneratedContent):
            raise TypeError(
                "content must be a GeneratedContent instance."
            )

        errors: list[str] = []
        warnings: list[str] = []

        text = content.content.strip()
        normalized_text = text.casefold()

        if not text:
            errors.append("Generated content is empty.")

        word_count = len(text.split())

        if word_count < self.config.min_word_count:
            errors.append(
                f"Content contains {word_count} words; "
                f"minimum required is {self.config.min_word_count}."
            )

        if word_count > self.config.max_word_count:
            errors.append(
                f"Content contains {word_count} words; "
                f"maximum allowed is {self.config.max_word_count}."
            )

        if (
            not self.config.allow_empty_title
            and (content.title is None or not content.title.strip())
        ):
            errors.append("Content title is required.")

        if (
            not self.config.allow_empty_description
            and (
                content.description is None
                or not content.description.strip()
            )
        ):
            errors.append("Content description is required.")

        for phrase in self.config.required_phrases:
            if phrase.casefold() not in normalized_text:
                errors.append(
                    f"Required phrase is missing: {phrase}"
                )

        for phrase in self.config.prohibited_phrases:
            if phrase.casefold() in normalized_text:
                errors.append(
                    f"Prohibited phrase found: {phrase}"
                )

        if content.word_count != word_count:
            warnings.append(
                "Stored word count does not match the content."
            )

        if content.character_count != len(content.content):
            warnings.append(
                "Stored character count does not match the content."
            )

        return ContentValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )

    def validate_many(
        self,
        contents: Sequence[GeneratedContent],
    ) -> list[ContentValidationResult]:
        """Validate multiple generated-content objects."""

        if isinstance(contents, (str, bytes)):
            raise TypeError(
                "contents must be a sequence of GeneratedContent objects."
            )

        if not isinstance(contents, Sequence):
            raise TypeError("contents must be a sequence.")

        return [
            self.validate(content)
            for content in contents
        ]

    def validate_result(
        self,
        result: GenerationResult,
    ) -> ContentValidationResult:
        """Validate a complete generation result."""

        if not isinstance(result, GenerationResult):
            raise TypeError(
                "result must be a GenerationResult instance."
            )

        errors: list[str] = []
        warnings: list[str] = []

        if result.status == GenerationStatus.COMPLETED:
            if result.generated_content is None:
                errors.append(
                    "Completed generation result has no generated content."
                )
            else:
                content_result = self.validate(
                    result.generated_content
                )
                errors.extend(content_result.errors)
                warnings.extend(content_result.warnings)

        elif result.status == GenerationStatus.FAILED:
            if not result.error:
                warnings.append(
                    "Failed generation result has no error description."
                )

        elif result.status == GenerationStatus.PENDING:
            warnings.append(
                "Generation has not started yet."
            )

        elif result.status == GenerationStatus.IN_PROGRESS:
            warnings.append(
                "Generation is still in progress."
            )

        elif result.status == GenerationStatus.CANCELLED:
            warnings.append(
                "Generation was cancelled."
            )

        return ContentValidationResult(
            is_valid=not errors,
            errors=errors,
            warnings=warnings,
        )


def validate_generated_content(
    content: GeneratedContent,
    config: ContentValidationConfig | None = None,
) -> ContentValidationResult:
    """Convenience function for validating generated content."""

    return GeneratedContentValidator(config).validate(content)


def validate_generation_result(
    result: GenerationResult,
    config: ContentValidationConfig | None = None,
) -> ContentValidationResult:
    """Convenience function for validating generation results."""

    return GeneratedContentValidator(config).validate_result(result)
