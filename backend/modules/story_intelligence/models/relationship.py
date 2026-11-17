
from typing import Literal

from pydantic import BaseModel, Field


RelationshipType = Literal[
    "PARENT_OF",
    "CHILD_OF",
    "SIBLING_OF",
    "SPOUSE_OF",
    "FRIEND_OF",
    "ALLY_OF",
    "ENEMY_OF",
    "RIVAL_OF",
    "MENTOR_OF",
    "STUDENT_OF",
    "BETRAYS",
    "PROTECTS",
    "WORKS_WITH",
    "KNOWS",
    "ROMANTIC_INTEREST_OF",
    "OTHER",
]


class RelationshipEvidence(BaseModel):
    """
    Stores evidence supporting a character relationship.
    """

    quote: str = Field(
        description="Exact quote from the original story."
    )

    evidence_type: Literal["explicit", "inferred"] = Field(
        description="Whether the relationship is stated or inferred."
    )


class CharacterRelationship(BaseModel):
    """
    Represents a relationship between two characters.
    """

    source_character: str = Field(
        description="Canonical name of the first character."
    )

    target_character: str = Field(
        description="Canonical name of the second character."
    )

    relationship_type: RelationshipType = Field(
        description="The type of relationship between characters."
    )

    description: str = Field(
        default="",
        description="A brief explanation of the relationship."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1."
    )

    evidence: list[RelationshipEvidence] = Field(
        default_factory=list,
        description="Supporting evidence from the story."
    )


class RelationshipExtractionResult(BaseModel):
    """
    Contains all relationships extracted from a story.
    """

    relationships: list[CharacterRelationship] = Field(
        default_factory=list,
        description="Relationships discovered in the story."
    )
