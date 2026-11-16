"""
Domain value objects.

Defines immutable, validated objects representing reusable
domain values such as language, region, scores, and time ranges.
"""

import math
import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ValueObject(BaseModel):
    """Base class for immutable domain value objects."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class LanguageCode(ValueObject):
    """Represents a language code."""

    value: str = Field(min_length=2, max_length=12)

    @field_validator("value")
    @classmethod
    def validate_language_code(cls, value: str) -> str:
        if not re.fullmatch(r"[a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,8})*", value):
            raise ValueError("Invalid language code.")
        return value.lower()


class RegionCode(ValueObject):
    """Represents a two-letter ISO-style country region code."""

    value: str = Field(min_length=2, max_length=2)

    @field_validator("value")
    @classmethod
    def validate_region_code(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Region must contain only alphabetic characters.")
        return value.upper()


class RelevanceScore(ValueObject):
    """Represents a normalized relevance score between zero and one."""

    value: float = Field(ge=0.0, le=1.0)

    @field_validator("value")
    @classmethod
    def validate_finite_score(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Relevance score must be finite.")
        return value


class TrendTimeRange(ValueObject):
    """Represents a UTC time interval for trend collection."""

    start_time: datetime
    end_time: datetime

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Datetime must include timezone information.")
        return value.astimezone(timezone.utc)

    @field_validator("end_time")
    @classmethod
    def validate_time_order(
        cls,
        end_time: datetime,
        info,
    ) -> datetime:
        start_time = info.data.get("start_time")

        if start_time is not None and end_time <= start_time:
            raise ValueError("End time must be later than start time.")

        return end_time


class DocumentMetadata(ValueObject):
    """Represents standardized document metadata."""

    language: LanguageCode = Field(
        default_factory=lambda: LanguageCode(value="en")
    )
    region: RegionCode = Field(
        default_factory=lambda: RegionCode(value="IN")
    )
    author: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=100)
    tags: tuple[str, ...] = ()


class SourceReference(ValueObject):
    """References an original document, trend, or news record."""

    source_id: str = Field(min_length=1, max_length=128)
    source_type: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=500)


__all__ = [
    "ValueObject",
    "LanguageCode",
    "RegionCode",
    "RelevanceScore",
    "TrendTimeRange",
    "DocumentMetadata",
    "SourceReference",
]
