"""
LLM provider interfaces.

Defines a common contract for language model integrations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


class LLMProvider(ABC):
    """Abstract contract for language model providers."""

    @abstractmethod
    def connect(self) -> None:
        """Initialize the provider connection."""
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """Check whether the provider is operational."""
        raise NotImplementedError

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for a single request."""
        raise NotImplementedError

    @abstractmethod
    def generate_many(
        self,
        requests: Sequence[LLMRequest],
    ) -> list[LLMResponse]:
        """Generate responses for multiple requests."""
        raise NotImplementedError

    def close(self) -> None:
        """Release provider resources when applicable."""
        return None
