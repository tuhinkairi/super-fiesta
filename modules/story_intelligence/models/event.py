
from uuid import uuid4
from typing import Literal

from pydantic import BaseModel, Field


class EventEvidence(BaseModel):
    """
    Evidence supporting an extracted story event.
    """

    quote: str = Field(
        description="Exact quote from the original story."
    )

    evidence_type: Literal["explicit", "inferred"] = Field(
        description="Whether the event is directly stated or inferred."
    )


class StoryEvent(BaseModel):
    """
    Represents one event occurring in a story.
    """

    event_id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    title: str = Field(
        description="Short name describing the event."
    )

    description: str = Field(
        default="",
        description="What happened during the event."
    )

    participants: list[str] = Field(
        default_factory=list,
        description="Canonical character names involved."
    )

    location: str | None = Field(
        default=None,
        description="Story location, if known."
    )

    chapter_number: int | None = Field(
        default=None,
        ge=1,
        description="Chapter in which the event occurs."
    )

    sequence_index: int = Field(
        ge=1,
        description="Position of the event in the supplied passage."
    )

    time_reference: str | None = Field(
        default=None,
        description="Original time expression from the story."
    )

    chronology_basis: Literal[
        "explicit_time",
        "narrative_order",
        "unknown"
    ] = "unknown"

    evidence: list[EventEvidence] = Field(
        default_factory=list,
        description="Original text supporting the event."
    )


class EventExtractionResult(BaseModel):
    """
    Collection of events extracted from a story.
    """

    events: list[StoryEvent] = Field(
        default_factory=list
    )
