"""
LLM provider and service factories.

Creates configured LLM providers and services.
"""

from __future__ import annotations

from context_aware_suggestion_rag.config.llm_config import (
    get_llm_config,
)
from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.gemini import GeminiProvider
from context_aware_suggestion_rag.llm.service import LLMService


def create_llm_provider(
    provider_name: str | None = None,
) -> BaseLLMProvider:
    """
    Create an LLM provider.

    Args:
        provider_name: Provider identifier. If omitted,
            the configured provider is used.

    Returns:
        An initialized provider instance.

    Raises:
        ValueError: If the provider is unsupported.
    """

    config = get_llm_config()

    selected_provider = (
        provider_name or config.provider
    ).strip().lower()

    if selected_provider in {"gemini", "google", "google_gemini"}:
        return GeminiProvider()

    raise ValueError(
        f"Unsupported LLM provider: {selected_provider}"
    )


def create_llm_service(
    provider: BaseLLMProvider | None = None,
) -> LLMService:
    """
    Create an LLM service.

    Args:
        provider: Optional custom provider. If omitted,
            the configured provider is created automatically.

    Returns:
        Configured LLMService instance.
    """

    selected_provider = (
        provider
        if provider is not None
        else create_llm_provider()
    )

    return LLMService(
        provider=selected_provider,
    )
