
from typing import Any, Literal

from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """
    Represents an entity inside the story graph.
    """

    id: str

    node_type: Literal[
        "character",
        "event",
        "location",
    ]

    label: str

    properties: dict[str, Any] = Field(
        default_factory=dict
    )


class GraphEdge(BaseModel):
    """
    Represents a relationship between two graph nodes.
    """

    id: str

    source_id: str

    target_id: str

    edge_type: str

    directed: bool = True

    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    evidence: list[str] = Field(
        default_factory=list
    )

    properties: dict[str, Any] = Field(
        default_factory=dict
    )


class StoryKnowledgeGraph(BaseModel):
    """
    Complete structured representation of a story graph.
    """

    project_id: str

    nodes: list[GraphNode] = Field(
        default_factory=list
    )

    edges: list[GraphEdge] = Field(
        default_factory=list
    )

    approval_status: Literal[
        "pending",
        "approved",
    ] = "pending"

    validation_warnings: list[str] = Field(
        default_factory=list
    )
