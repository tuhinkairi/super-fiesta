
"""
Models for the content generation module.

Defines generation requests, generated content, execution results,
and associated metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any
from uuid import uuid4


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class GenerationStatus(str, Enum):
    """Possible states of a content-generation operation."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationMode(str, Enum):
    """Generation execution modes."""

    SINGLE = "single"
    BATCH = "batch"
    STREAMING = "streaming"


@dataclass(slots=True)
class GenerationParameters:
    """Controls model behavior during content generation."""

    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: int = 2048
    candidate_count: int = 1
    stop_sequences: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if (
            isinstance(self.temperature, bool)
            or not isinstance(self.temperature, (int, float))
            or not math.isfinite(self.temperature)
            or not 0.0 <= self.temperature <= 2.0
        ):
            raise ValueError(
                "temperature must be a finite number between 0 and 2."
            )

        if (
            isinstance(self.top_p, bool)
            or not isinstance(self.top_p, (int, float))
            or not math.isfinite(self.top_p)
            or not 0.0 < self.top_p <= 1.0
        ):
            raise ValueError(
                "top_p must be a finite number greater than 0 and at most 1."
            )

        if (
            isinstance(self.top_k, bool)
            or not isinstance(self.top_k, int)
            or self.top_k <= 0
        ):
            raise ValueError("top_k must be a positive integer.")

        if (
            isinstance(self.max_output_tokens, bool)
            or not isinstance(self.max_output_tokens, int)
            or self.max_output_tokens <= 0
        ):
            raise ValueError(
                "max_output_tokens must be a positive integer."
            )

        if (
            isinstance(self.candidate_count, bool)
            or not isinstance(self.candidate_count, int)
            or self.candidate_count <= 0
        ):
            raise ValueError(
                "candidate_count must be a positive integer."
            )

        if not isinstance(self.stop_sequences, list):
            raise TypeError("stop_sequences must be a list.")

        if any(
            not isinstance(sequence, str) or not sequence.strip()
            for sequence in self.stop_sequences
        ):
            raise ValueError(
                "Every stop sequence must be a non-empty string."
            )


@dataclass(slots=True)
class GenerationRequest:
    """Input request for generating content."""

    prompt: str
    recommendation_id: str | None = None
    content_format: str = "article"
    target_audience: str = "general audience"
    language: str = "en"
    region: str = "IN"
    parameters: GenerationParameters = field(
        default_factory=GenerationParameters
    )
    context: str | None = None
    instructions: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(
        default_factory=lambda: f"genreq_{uuid4().hex}"
    )
    created_at: datetime = field(default_factory=current_utc_time)

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str) or not self.prompt.strip():
            raise ValueError("prompt must be a non-empty string.")

        if self.recommendation_id is not None:
            if (
                not isinstance(self.recommendation_id, str)
                or not self.recommendation_id.strip()
            ):
                raise ValueError(
                    "recommendation_id must be a non-empty string or None."
                )

        for field_name in (
            "content_format",
            "target_audience",
            "language",
            "region",
            "request_id",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(self.parameters, GenerationParameters):
            raise TypeError(
                "parameters must be a GenerationParameters instance."
            )

        if self.context is not None and not isinstance(self.context, str):
            raise TypeError("context must be a string or None.")

        if self.instructions is not None:
            if not isinstance(self.instructions, str):
                raise TypeError("instructions must be a string or None.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")


@dataclass(slots=True)
class GeneratedContent:
    """Represents content produced by an LLM."""

    content: str
    request_id: str
    content_format: str
    model: str
    recommendation_id: str | None = None
    title: str | None = None
    description: str | None = None
    language: str = "en"
    word_count: int = field(init=False)
    character_count: int = field(init=False)
    content_id: str = field(
        default_factory=lambda: f"content_{uuid4().hex}"
    )
    generated_at: datetime = field(default_factory=current_utc_time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("content must be a non-empty string.")

        for field_name in (
            "request_id",
            "content_format",
            "model",
            "language",
            "content_id",
        ):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if self.recommendation_id is not None:
            if (
                not isinstance(self.recommendation_id, str)
                or not self.recommendation_id.strip()
            ):
                raise ValueError(
                    "recommendation_id must be a non-empty string or None."
                )

        if self.title is not None and not isinstance(self.title, str):
            raise TypeError("title must be a string or None.")

        if self.description is not None:
            if not isinstance(self.description, str):
                raise TypeError("description must be a string or None.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if not isinstance(self.generated_at, datetime):
            raise TypeError("generated_at must be a datetime.")

        self.word_count = len(self.content.split())
        self.character_count = len(self.content)


@dataclass(slots=True)
class GenerationResult:
    """Result of a content-generation operation."""

    request_id: str
    status: GenerationStatus
    generated_content: GeneratedContent | None = None
    error: str | None = None
    execution_time_ms: float = 0.0
    model: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.request_id, str) or not self.request_id.strip():
            raise ValueError("request_id must be a non-empty string.")

        if not isinstance(self.status, GenerationStatus):
            self.status = GenerationStatus(self.status)

        if self.generated_content is not None:
            if not isinstance(self.generated_content, GeneratedContent):
                raise TypeError(
                    "generated_content must be GeneratedContent or None."
                )

            if self.generated_content.request_id != self.request_id:
                raise ValueError(
                    "Generated content request_id must match the result."
                )

        if (
            isinstance(self.execution_time_ms, bool)
            or not isinstance(self.execution_time_ms, (int, float))
            or not math.isfinite(self.execution_time_ms)
            or self.execution_time_ms < 0
        ):
            raise ValueError(
                "execution_time_ms must be a finite non-negative number."
            )

        if self.model is not None:
            if not isinstance(self.model, str) or not self.model.strip():
                raise ValueError("model must be a non-empty string or None.")

        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("error must be a string or None.")

        if not isinstance(self.warnings, list):
            raise TypeError("warnings must be a list.")

        if any(not isinstance(item, str) for item in self.warnings):
            raise TypeError("Every warning must be a string.")

        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary.")

        if self.completed_at is not None:
            if not isinstance(self.completed_at, datetime):
                raise TypeError("completed_at must be a datetime.")

    @property
    def success(self) -> bool:
        """Return whether generation completed successfully."""

        return (
            self.status == GenerationStatus.COMPLETED
            and self.generated_content is not None
            and self.error is None
        )


@dataclass(slots=True)
class GenerationBatchResult:
    """Aggregated result of multiple generation requests."""

    results: list[GenerationResult] = field(default_factory=list)
    batch_id: str = field(
        default_factory=lambda: f"genbatch_{uuid4().hex}"
    )
    created_at: datetime = field(default_factory=current_utc_time)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def successful(self) -> int:
        return sum(result.success for result in self.results)

    @property
    def failed(self) -> int:
        return sum(
            result.status == GenerationStatus.FAILED
            for result in self.results
        )

    @property
    def pending(self) -> int:
        return sum(
            result.status == GenerationStatus.PENDING
            for result in self.results
        )

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0

        return self.successful / self.total

    def __post_init__(self) -> None:
        if not isinstance(self.results, list):
            raise TypeError("results must be a list.")

        if any(
            not isinstance(result, GenerationResult)
            for result in self.results
        ):
            raise TypeError(
                "Every batch result must be a GenerationResult."
            )

        if not isinstance(self.batch_id, str) or not self.batch_id.strip():
            raise ValueError("batch_id must be a non-empty string.")

        if not isinstance(self.created_at, datetime):
            raise TypeError("created_at must be a datetime.")
