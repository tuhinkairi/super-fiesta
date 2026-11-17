from typing import Literal

from pydantic import BaseModel, Field

from modules.story_intelligence.models.event import StoryEvent


class TimelineResult(BaseModel):
    """
    Represents an ordered collection of story events.
    """

    events: list[StoryEvent] = Field(
        default_factory=list,
        description="Events arranged using available story order information.",
    )

    ordering_method: Literal[
        "chapter_and_sequence",
        "narrative_sequence",
        "input_order",
    ] = "input_order"

    ordering_warnings: list[str] = Field(
        default_factory=list,
        description="Warnings about uncertain event ordering.",
    )

    chronology_verified: bool = False
