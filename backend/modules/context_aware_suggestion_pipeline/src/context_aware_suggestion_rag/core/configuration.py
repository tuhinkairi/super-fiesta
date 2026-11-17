"""
Centralized configuration access.

Provides a single entry point for loading all package
configuration objects.
"""

from dataclasses import dataclass
from functools import lru_cache

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.embedding_config import (
    EmbeddingConfig,
    get_embedding_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.llm_config import (
    LLMConfig,
    get_llm_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.pinecone_config import (
    PineconeConfig,
    get_pinecone_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.retrieval_config import (
    RetrievalConfig,
    get_retrieval_config,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.settings import (
    Settings,
    get_settings,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.trend_config import (
    TrendConfig,
    get_trend_config,
)


@dataclass(frozen=True, slots=True)
class ApplicationConfiguration:
    """
    Collection of all application configuration objects.

    Each configuration remains independently defined in its
    corresponding config module.
    """

    settings: Settings
    llm: LLMConfig
    pinecone: PineconeConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig
    trend: TrendConfig


@lru_cache(maxsize=1)
def get_application_configuration() -> ApplicationConfiguration:
    """
    Load and return the complete application configuration.

    The result is cached to avoid repeatedly constructing
    configuration objects.
    """

    return ApplicationConfiguration(
        settings=get_settings(),
        llm=get_llm_config(),
        pinecone=get_pinecone_config(),
        embedding=get_embedding_config(),
        retrieval=get_retrieval_config(),
        trend=get_trend_config(),
    )


def clear_configuration_cache() -> None:
    """
    Clear cached configuration objects.

    Useful in tests when environment variables change.
    """

    get_application_configuration.cache_clear()

    get_settings.cache_clear()
    get_llm_config.cache_clear()
    get_pinecone_config.cache_clear()
    get_embedding_config.cache_clear()
    get_retrieval_config.cache_clear()
    get_trend_config.cache_clear()


__all__ = [
    "ApplicationConfiguration",
    "get_application_configuration",
    "clear_configuration_cache",
]
