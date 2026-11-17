
from typing import Literal

from pydantic import BaseModel, Field


class CharacterEvidence(BaseModel):
    """
    Stores text evidence supporting a character fact.
    """

    fact: str = Field(
        description="The character fact supported by the evidence."
    )

    quote: str = Field(
        description="Exact words copied from the original story."
    )

    evidence_type: Literal["explicit", "inferred"] = Field(
        description="Whether the fact is directly stated or inferred."
    )


class Character(BaseModel):
    """
    Represents one character in a story.
    """

    name: str = Field(
        description="The primary name of the character."
    )

    aliases: list[str] = Field(
        default_factory=list,
        description="Other names used for the same character."
    )

    role_in_story: str = Field(
        default="unknown",
        description="The character's role, only when supported by text."
    )

    description: str = Field(
        default="",
        description="A factual description based on the story."
    )

    personality_traits: list[str] = Field(
        default_factory=list,
        description="Personality traits supported by the story."
    )

    evidence: list[CharacterEvidence] = Field(
        default_factory=list,
        description="Evidence supporting extracted character facts."
    )


class CharacterExtractionResult(BaseModel):
    """
    Contains all characters extracted from a story passage.
    """

    characters: list[Character] = Field(
        default_factory=list,
        description="Characters found in the supplied story."
    )
