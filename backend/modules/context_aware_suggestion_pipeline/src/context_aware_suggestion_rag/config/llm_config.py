"""
Gemini LLM configuration.

Defines model selection, authentication, generation parameters,
and request-level settings for Google Gemini.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_ENV = Path(__file__).resolve().parents[6] / ".env"


class LLMConfig(BaseSettings):
    """Configuration for the Gemini language model provider."""

    # --------------------------------------------------------
    # Provider
    # --------------------------------------------------------

    provider: Literal["gemini"] = "gemini"

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    api_key: SecretStr | None = Field(
        default=None,
        validation_alias="GEMINI_API_KEY",
    )

    # --------------------------------------------------------
    # Model Selection
    # --------------------------------------------------------

    model_name: str = Field(
        default="gemini-3.8-flash", validation_alias="SUGGESTION_MODEL"
    )

    # --------------------------------------------------------
    # Generation Parameters
    # --------------------------------------------------------

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
    )

    max_output_tokens: int = Field(
        default=4096,
        ge=1,
    )

    top_p: float = Field(
        default=0.95,
        gt=0.0,
        le=1.0,
    )

    top_k: int | None = Field(
        default=40,
        ge=1,
    )

    # --------------------------------------------------------
    # Request Configuration
    # --------------------------------------------------------

    timeout_seconds: int = Field(
        default=60,
        ge=1,
    )

    max_retries: int = Field(
        default=3,
        ge=0,
    )

    # --------------------------------------------------------
    # Structured Output
    # --------------------------------------------------------

    response_mime_type: Literal[
        "text/plain",
        "application/json",
    ] = "text/plain"

    # --------------------------------------------------------
    # Environment Configuration
    # --------------------------------------------------------

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV,
        env_file_encoding="utf-8",
        env_prefix="CASR_LLM_",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    @property
    def is_configured(self) -> bool:
        """Check whether a Gemini API key has been supplied."""

        return (
            self.api_key is not None
            and bool(self.api_key.get_secret_value().strip())
        )


@lru_cache(maxsize=1)
def get_llm_config() -> LLMConfig:
    """Return a cached Gemini configuration instance."""

    return LLMConfig()


__all__ = [
    "LLMConfig",
    "get_llm_config",
]
