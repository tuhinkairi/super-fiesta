"""
Content generation service.

Coordinates generation providers, output validation,
and content formatting.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.formatter import (
    ContentFormatter,
    FormattingOptions,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
    GenerationRequest,
    GenerationResult,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.validators import (
    GeneratedContentValidator,
    ContentValidationResult,
)


class GenerationService:
    """Orchestrates content generation and output processing."""

    def __init__(
        self,
        provider: BaseGenerationProvider,
        *,
        validator: GeneratedContentValidator | None = None,
        formatter: ContentFormatter | None = None,
    ) -> None:
        if not isinstance(provider, BaseGenerationProvider):
            raise TypeError(
                "provider must implement BaseGenerationProvider."
            )

        self.provider = provider
        self.validator = validator or GeneratedContentValidator()
        self.formatter = formatter or ContentFormatter()

    def generate(
        self,
        request: GenerationRequest,
        *,
        validate: bool = True,
    ) -> GenerationResult:
        """Generate and optionally validate a single result."""

        if not isinstance(request, GenerationRequest):
            raise TypeError("request must be a GenerationRequest.")

        result = self.provider.generate(request)

        if not isinstance(result, GenerationResult):
            raise TypeError(
                "Generation provider must return GenerationResult."
            )

        if validate and result.generated_content is not None:
            validation = self.validator.validate(
                result.generated_content
            )

            if not validation.is_valid:
                result.warnings.extend(validation.errors)

        return result

    def generate_many(
        self,
        requests: Sequence[GenerationRequest],
        *,
        validate: bool = True,
    ) -> list[GenerationResult]:
        """Generate and optionally validate multiple results."""

        if isinstance(requests, (str, bytes)):
            raise TypeError("requests must be a sequence of GenerationRequest objects.")

        if not isinstance(requests, Sequence):
            raise TypeError("requests must be a sequence.")

        if not all(
            isinstance(request, GenerationRequest)
            for request in requests
        ):
            raise TypeError(
                "Every item must be a GenerationRequest."
            )

        results = self.provider.generate_many(requests)

        if not isinstance(results, list):
            raise TypeError(
                "Generation provider must return a list of GenerationResult objects."
            )

        if len(results) != len(requests):
            raise ValueError(
                "Provider must return one result for each request."
            )

        if not all(
            isinstance(result, GenerationResult)
            for result in results
        ):
            raise TypeError(
                "Every result must be a GenerationResult."
            )

        if validate:
            for result in results:
                if result.generated_content is None:
                    continue

                validation = self.validator.validate(
                    result.generated_content
                )

                if not validation.is_valid:
                    result.warnings.extend(validation.errors)

        return results

    
    def format_content(
        self,
        content: GeneratedContent,
        output_format: str = "markdown",
    ) -> str:
        """Format generated content into the requested output format."""

        if not isinstance(content, GeneratedContent):
            raise TypeError(
                "content must be a GeneratedContent instance."
            )

        return self.formatter.format(
            content,
            output_format,
        )

    def validate_content(
        self,
        content: GeneratedContent,
    ) -> ContentValidationResult:
        """Validate generated content independently."""

        if not isinstance(content, GeneratedContent):
            raise TypeError(
                "content must be a GeneratedContent instance."
            )

        return self.validator.validate(content)

    def health_check(self) -> bool:
        """Check whether the generation provider is healthy."""

        try:
            return bool(
                self.provider.connect()
                and self.provider.health_check()
            )
        except Exception:
            return False

    
    def close(self) -> None:
        """Close the underlying generation provider if supported."""

        close_method = getattr(self.provider, "close", None)

        if callable(close_method):
            close_method()

