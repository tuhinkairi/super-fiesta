
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenerationRequest(BaseModel):
    """Represents a request to generate a GraphRAG answer."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)

    context: str = Field(default="")

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_output_tokens: int = Field(
        default=2048,
        ge=1,
        le=8192,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty.")
        return value

    @field_validator("context")
    @classmethod
    def normalize_context(cls, value: str) -> str:
        return value.strip()


class GenerationResult(BaseModel):
    """Represents the generated answer."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    model: str = Field(min_length=1)

    context_used: bool = True

    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: dict[str, str | int | float | bool] = Field(
        default_factory=dict
    )

    @field_validator("query", "answer", "model")
    @classmethod
    def validate_non_empty_strings(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be empty.")
        return value
