"""Configuration package public exports."""

from pathlib import Path

from dotenv import load_dotenv

ROOT_ENV = Path(__file__).resolve().parents[6] / ".env"
load_dotenv(ROOT_ENV, override=False)

from .embedding_config import get_embedding_config
from .llm_config import get_llm_config
from .pinecone_config import get_pinecone_config
from .retrieval_config import get_retrieval_config
from .trend_config import get_trend_config

from .validation import (
    ConfigurationIssue,
    ConfigurationValidationResult,
    ConfigurationValidator,
    validate_configuration,
)

__all__ = [
    "get_embedding_config",
    "get_llm_config",
    "get_pinecone_config",
    "get_retrieval_config",
    "get_trend_config",
    "ConfigurationIssue",
    "ConfigurationValidationResult",
    "ConfigurationValidator",
    "validate_configuration",
]
