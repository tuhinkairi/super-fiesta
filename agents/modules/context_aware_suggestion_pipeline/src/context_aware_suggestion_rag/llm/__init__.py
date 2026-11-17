"""
LLM integration package.

Provides standardized language model interfaces,
Gemini integration, services, and factories.
"""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.base import (
    BaseLLMProvider,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.gemini import (
    GeminiProvider,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.service import (
    LLMService,
)

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.factory import (
    create_llm_provider,
    create_llm_service,
)


__all__ = [
    # Models
    "LLMRequest",
    "LLMResponse",
    "LLMUsage",

    # Provider interface
    "BaseLLMProvider",

    # Gemini
    "GeminiProvider",

    # Service
    "LLMService",

    # Factories
    "create_llm_provider",
    "create_llm_service",
]
