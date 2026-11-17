from uuid import uuid4
from typing import Literal

from pydantic import BaseModel, Field

from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)


class SuggestionFinding(BaseModel):
    """
    Represents an issue or warning found during
    suggestion validation.
    """

    rule_id: str

    severity: Literal[
        "critical",
        "warning",
        "advisory",
    ]

    message: str

    involved_node_ids: list[str] = Field(default_factory=list)


class StorySuggestion(BaseModel):
    """
    Represents one hypothetical story direction.

    Suggestions remain separate from canonical story facts.
    """

    suggestion_id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    suggestion_type: Literal[
        "character_development",
        "relationship_change",
        "new_event",
        "plot_twist",
        "alternative_ending",
        "other",
    ] = "other"

    rationale: str = ""

    based_on_node_ids: list[str] = Field(default_factory=list)

    source_evidence: list[str] = Field(default_factory=list)

    proposed_nodes: list[GraphNode] = Field(default_factory=list)

    proposed_edges: list[GraphEdge] = Field(default_factory=list)

    guardrail_findings: list[SuggestionFinding] = Field(default_factory=list)

    status: Literal[
        "proposed",
        "approved",
        "rejected",
    ] = "proposed"

    approval_note: str = ""


class SuggestionGraph(BaseModel):
    """
    Stores hypothetical suggestions separately
    from the canonical knowledge graph.
    """

    project_id: str

    suggestions: list[StorySuggestion] = Field(default_factory=list)


class SuggestionApprovalResult(BaseModel):
    """
    Contains the result of an author approval decision.
    """

    action: Literal[
        "approved",
        "rejected",
    ]

    message: str

    canonical_graph: StoryKnowledgeGraph

    suggestion_graph: SuggestionGraph
