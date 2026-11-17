"""
Data models for LLM operations.

Provides provider-independent request and response structures
for language model integrations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def current_utc_time() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class LLMRequest:
    """Represents a request sent to a language model."""

    prompt: str
    system_instruction: str | None = None
    model: str | None = None
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 2048
    stop_sequences: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("prompt must be a non-empty string.")

        if self.system_instruction is not None:
            if not isinstance(self.system_instruction, str):
                raise TypeError(
                    "system_instruction must be a string or None."
                )

        if self.model is not None:
            if not isinstance(self.model, str) or not self.model.strip():
                raise ValueError("model must be a non-empty string or None.")

        if not isinstance(self.temperature, (int, float)):
            raise TypeError("temperature must be numeric.")

        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2.")

        if not isinstance(self.top_p, (int, float)):
            raise TypeError("top_p must be numeric.")

        if not 0.0 < self.top_p <= 1.0:
            raise ValueError("top_p must be greater than 0 and at most 1.")

        if isinstance(self.top_k, bool) or not isinstance(self.top_k, int):
            raise TypeError("top_k must be an integer.")

        if self.top_k < 1:
            raise ValueError("top_k must be positive.")

        if (
            isinstance(self.max_output_tokens, bool)
            or not isinstance(self.max_output_tokens, int)
        ):
            raise TypeError("max_output_tokens must be an integer.")

        if self.max_output_tokens < 1:
            raise ValueError("max_output_tokens must be positive.")

        if not isinstance(self.stop_sequences, list):
            raise TypeError("stop_sequences must be a list.")

        if not all(
            isinstance(item, str) and item
            for item in self.stop_sequences
        ):
            raise ValueError(
                "Every stop sequence must be a non-empty string."
            )

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")


@dataclass(slots=True)
class LLMUsage:
    """Token usage information returned by an LLM."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
        ):
            value = getattr(self, field_name)

            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer.")

            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.total_tokens == 0:
            self.total_tokens = (
                self.prompt_tokens + self.completion_tokens
            )


@dataclass(slots=True)
class LLMResponse:
    """Represents a standardized language model response."""

    text: str
    model: str
    provider: str
    usage: LLMUsage = field(default_factory=LLMUsage)
    finish_reason: str | None = None
    latency_ms: float = 0.0
    created_at: datetime = field(default_factory=current_utc_time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.text, str):
            raise TypeError("text must be a string.")

        if not isinstance(self.model, str) or not self.model.strip():
            raise ValueError("model must be a non-empty string.")

        if not isinstance(self.provider, str) or not self.provider.strip():
            raise ValueError("provider must be a non-empty string.")

        if not isinstance(self.usage, LLMUsage):
            raise TypeError("usage must be an LLMUsage instance.")

        if not isinstance(self.latency_ms, (int, float)):
            raise TypeError("latency_ms must be numeric.")

        if self.latency_ms < 0:
            raise ValueError("latency_ms cannot be negative.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")
