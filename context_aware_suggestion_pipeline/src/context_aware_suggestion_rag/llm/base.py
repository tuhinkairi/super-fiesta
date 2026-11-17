"""
Abstract interfaces for language model providers.

Defines the common contract for LLM integrations.
"""

from __future__ import annotations

from abc import abstractmethod
from collections.abc import Sequence

from context_aware_suggestion_rag.core.base import BaseProvider
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


class BaseLLMProvider(BaseProvider):
    """Abstract base class for language model providers."""

    @abstractmethod
    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """
        Generate a response for a single LLM request.

        Args:
            request: Standardized LLM request.

        Returns:
            Standardized LLM response.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_many(
        self,
        requests: Sequence[LLMRequest],
    ) -> list[LLMResponse]:
        """
        Generate responses for multiple requests.

        Args:
            requests: Sequence of LLM requests.

        Returns:
            List of LLM responses.
        """
        raise NotImplementedError
