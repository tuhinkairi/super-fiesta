
"""
Abstract interfaces for content generation providers.

Defines the common contract that concrete generation providers
must implement, regardless of the underlying LLM or API.
"""

from __future__ import annotations

from abc import abstractmethod

from context_aware_suggestion_rag.core.base import BaseProvider
from context_aware_suggestion_rag.generation.models import (
    GenerationBatchResult,
    GenerationRequest,
    GenerationResult,
)


class BaseGenerationProvider(BaseProvider):
    """Abstract interface for content generation providers."""

    @abstractmethod
    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Generate content for a single request.

        Args:
            request: The generation request.

        Returns:
            The result of the generation operation.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_many(
        self,
        requests: list[GenerationRequest],
    ) -> GenerationBatchResult:
        """
        Generate content for multiple requests.

        Args:
            requests: A list of generation requests.

        Returns:
            A batch result containing individual generation results.
        """
        raise NotImplementedError
