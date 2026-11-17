
from modules.story_intelligence.models.graph import (
    StoryKnowledgeGraph,
    GraphEdge,
)

from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionFinding,
)


class GuardrailEngine:
    """
    Checks hypothetical story suggestions against
    established canonical story facts.

    This engine does not modify the canonical graph.
    """

    # Relationships that may conflict when they connect
    # the same two characters.
    INCOMPATIBLE_RELATIONSHIPS = {
        frozenset({"FRIEND_OF", "ENEMY_OF"}),
        frozenset({"ALLY_OF", "ENEMY_OF"}),
    }

    def __init__(self, canonical_graph: StoryKnowledgeGraph):

        self.canonical_graph = canonical_graph

        # Create a lookup for canonical graph nodes.
        self.canonical_nodes = {
            node.id: node
            for node in canonical_graph.nodes
        }

        if len(self.canonical_nodes) != len(
            canonical_graph.nodes
        ):
            raise ValueError(
                "Canonical graph contains duplicate node IDs."
            )

    @staticmethod
    def _normalize_label(value: str) -> str:
        return " ".join(value.casefold().split())

    @staticmethod
    def _same_relationship_pair(
        first: GraphEdge,
        second: GraphEdge,
    ) -> bool:
        """
        Check whether two relationship edges connect
        the same pair of nodes.
        """

        if first.directed or second.directed:
            return (
                first.source_id == second.source_id
                and first.target_id == second.target_id
            )

        return (
            {first.source_id, first.target_id}
            == {second.source_id, second.target_id}
        )

    def validate(
        self,
        suggestion: StorySuggestion,
    ) -> StorySuggestion:
        """
        Inspect a suggestion and return a copy containing
        guardrail findings.
        """

        findings = []

        def add_finding(
            rule_id: str,
            severity: str,
            message: str,
            node_ids: list[str] | None = None,
        ):
            findings.append(
                SuggestionFinding(
                    rule_id=rule_id,
                    severity=severity,
                    message=message,
                    involved_node_ids=node_ids or [],
                )
            )

        canonical_ids = set(self.canonical_nodes)

        proposed_node_ids = {
            node.id for node in suggestion.proposed_nodes
        }

        # ------------------------------------------------
        # 1. Check references to canonical nodes.
        # ------------------------------------------------

        for node_id in suggestion.based_on_node_ids:

            if node_id not in canonical_ids:
                add_finding(
                    rule_id="UNKNOWN_CANONICAL_REFERENCE",
                    severity="critical",
                    message=(
                        f"Suggestion references unknown canonical "
                        f"node: {node_id}"
                    ),
                    node_ids=[node_id],
                )

        # ------------------------------------------------
        # 2. Check for duplicate proposed nodes.
        # ------------------------------------------------

        canonical_labels = {
            (
                node.node_type,
                self._normalize_label(node.label),
            ): node
            for node in self.canonical_nodes.values()
        }

        for node in suggestion.proposed_nodes:

            if node.id in canonical_ids:
                add_finding(
                    rule_id="CANONICAL_NODE_ID_COLLISION",
                    severity="critical",
                    message=(
                        f"Proposed node ID collides with a canonical "
                        f"node: {node.id}"
                    ),
                    node_ids=[node.id],
                )

            key = (
                node.node_type,
                self._normalize_label(node.label),
            )

            existing = canonical_labels.get(key)

            if existing is not None:
                add_finding(
                    rule_id="POSSIBLE_DUPLICATE_NODE",
                    severity="warning",
                    message=(
                        f"Proposed node '{node.label}' may duplicate "
                        f"existing canonical node '{existing.label}'."
                    ),
                    node_ids=[existing.id, node.id],
                )

        # ------------------------------------------------
        # 3. Check proposed graph edges.
        # ------------------------------------------------

        valid_node_ids = canonical_ids | proposed_node_ids

        canonical_relationships = [
            edge
            for edge in self.canonical_graph.edges
            if edge.edge_type not in {
                "PARTICIPATED_IN",
                "OCCURRED_AT",
            }
        ]

        for edge in suggestion.proposed_edges:

            if (
                edge.source_id not in valid_node_ids
                or edge.target_id not in valid_node_ids
            ):
                add_finding(
                    rule_id="INVALID_PROPOSED_EDGE",
                    severity="critical",
                    message=(
                        f"Proposed edge '{edge.id}' references "
                        "a node that does not exist."
                    ),
                    node_ids=[
                        edge.source_id,
                        edge.target_id,
                    ],
                )
                continue

            if edge.source_id == edge.target_id:
                add_finding(
                    rule_id="SELF_RELATIONSHIP",
                    severity="critical",
                    message=(
                        "A proposed relationship connects "
                        "a node to itself."
                    ),
                    node_ids=[edge.source_id],
                )
                continue

            # Only compare relationships whose endpoints
            # already exist in the canonical graph.
            if (
                edge.source_id in canonical_ids
                and edge.target_id in canonical_ids
            ):

                for existing_edge in canonical_relationships:

                    if not self._same_relationship_pair(
                        edge,
                        existing_edge,
                    ):
                        continue

                    relationship_pair = frozenset({
                        edge.edge_type,
                        existing_edge.edge_type,
                    })

                    if relationship_pair in self.INCOMPATIBLE_RELATIONSHIPS:

                        add_finding(
                            rule_id="CONFLICTING_RELATIONSHIP",
                            severity="warning",
                            message=(
                                f"Proposed relationship "
                                f"'{edge.edge_type}' may conflict "
                                f"with the established relationship "
                                f"'{existing_edge.edge_type}'. "
                                "Review the story chronology before "
                                "approving this change."
                            ),
                            node_ids=[
                                edge.source_id,
                                edge.target_id,
                            ],
                        )

        # ------------------------------------------------
        # 4. Check whether the suggestion has grounding.
        # ------------------------------------------------

        if not suggestion.based_on_node_ids:
            add_finding(
                rule_id="MISSING_STORY_CONTEXT",
                severity="advisory",
                message=(
                    "The suggestion does not reference "
                    "any canonical story nodes."
                ),
            )

        if not suggestion.source_evidence:
            add_finding(
                rule_id="MISSING_SOURCE_EVIDENCE",
                severity="advisory",
                message=(
                    "No supporting story evidence was "
                    "attached to this suggestion."
                ),
            )

        # Preserve the original suggestion and return
        # a separate version containing validation findings.
        return suggestion.model_copy(
            update={
                "guardrail_findings": findings,
            }
        )
