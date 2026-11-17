"""
Generation provider interfaces.

Defines a provider-independent contract for content generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GenerationRequest,
    GenerationResult,
)


class GenerationProvider(ABC):
    """Abstract contract for content-generation providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider connection."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Generate content for a single request."""
        raise NotImplementedError

    @abstractmethod
    def generate_many(
        self,
        requests: Sequence[GenerationRequest],
    ) -> list[GenerationResult]:
        """Generate content for multiple requests."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
