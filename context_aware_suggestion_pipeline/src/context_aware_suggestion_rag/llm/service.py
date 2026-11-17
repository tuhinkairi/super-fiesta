"""
LLM service.

Provides a unified interface for interacting with language
model providers.
"""

from __future__ import annotations

from collections.abc import Sequence

from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
)


class LLMService:
    """Coordinates requests and responses from an LLM provider."""

    def __init__(
        self,
        provider: BaseLLMProvider,
    ) -> None:
        if not isinstance(provider, BaseLLMProvider):
            raise TypeError(
                "provider must implement BaseLLMProvider."
            )

        self.provider = provider

    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """Generate a response for a single request."""

        if not isinstance(request, LLMRequest):
            raise TypeError(
                "request must be an LLMRequest instance."
            )

        response = self.provider.generate(request)

        if not isinstance(response, LLMResponse):
            raise TypeError(
                "Provider must return an LLMResponse instance."
            )

        return response

    def generate_many(
        self,
        requests: Sequence[LLMRequest],
    ) -> list[LLMResponse]:
        """Generate responses for multiple requests."""

        if isinstance(requests, (str, bytes)):
            raise TypeError(
                "requests must be a sequence of LLMRequest objects."
            )

        if not isinstance(requests, Sequence):
            raise TypeError(
                "requests must be a sequence."
            )

        if not all(
            isinstance(request, LLMRequest)
            for request in requests
        ):
            raise TypeError(
                "Every item must be an LLMRequest instance."
            )

        responses = self.provider.generate_many(requests)

        if not isinstance(responses, list):
            raise TypeError(
                "Provider must return a list of LLMResponse objects."
            )

        if len(responses) != len(requests):
            raise ValueError(
                "Provider must return one response for each request."
            )

        if not all(
            isinstance(response, LLMResponse)
            for response in responses
        ):
            raise TypeError(
                "Every response must be an LLMResponse instance."
            )

        return responses

    def health_check(self) -> bool:
        """Check the health of the underlying provider."""

        try:
            return bool(
                self.provider.connect()
                and self.provider.health_check()
            )
        except Exception:
            return False

    def close(self) -> None:
        """Close the provider if it supports cleanup."""

        close_method = getattr(
            self.provider,
            "close",
            None,
        )

        if callable(close_method):
            close_method()
