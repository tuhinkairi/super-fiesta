from modules.story_intelligence.models.graph import (
    StoryKnowledgeGraph,
)

from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
    SuggestionApprovalResult,
)


class ApprovalManager:
    """
    Manages author approval and rejection of story suggestions.

    Approved suggestions are applied to a new canonical graph
    version. Rejected suggestions never modify the canonical graph.
    """

    def __init__(
        self,
        canonical_graph: StoryKnowledgeGraph,
        suggestion_graph: SuggestionGraph,
    ):

        if canonical_graph.approval_status != "approved":
            raise ValueError("Canonical graph must be approved.")

        if canonical_graph.project_id != suggestion_graph.project_id:
            raise ValueError("Both graphs must belong to the same project.")

        self.canonical_graph = canonical_graph
        self.suggestion_graph = suggestion_graph

    def get_suggestion(
        self,
        suggestion_id: str,
    ) -> StorySuggestion:
        """
        Retrieve a suggestion using its ID.
        """

        for suggestion in self.suggestion_graph.suggestions:

            if suggestion.suggestion_id == suggestion_id:
                return suggestion

        raise ValueError(f"Suggestion not found: {suggestion_id}")

    def _validate_changes(
        self,
        suggestion: StorySuggestion,
    ) -> None:
        """
        Validate proposed graph changes before approval.
        """

        canonical_node_ids = {node.id for node in self.canonical_graph.nodes}

        canonical_edge_ids = {edge.id for edge in self.canonical_graph.edges}

        # Validate references to existing canonical nodes.
        for node_id in suggestion.based_on_node_ids:

            if node_id not in canonical_node_ids:
                raise ValueError(f"Unknown canonical node reference: {node_id}")

        # Validate proposed node IDs.
        proposed_node_ids = [node.id for node in suggestion.proposed_nodes]

        if len(proposed_node_ids) != len(set(proposed_node_ids)):
            raise ValueError("Duplicate proposed node IDs.")

        if canonical_node_ids.intersection(proposed_node_ids):
            raise ValueError(
                "A proposed node ID already exists in the canonical graph."
            )

        # Validate proposed edge IDs.
        proposed_edge_ids = [edge.id for edge in suggestion.proposed_edges]

        if len(proposed_edge_ids) != len(set(proposed_edge_ids)):
            raise ValueError("Duplicate proposed edge IDs.")

        if canonical_edge_ids.intersection(proposed_edge_ids):
            raise ValueError(
                "A proposed edge ID already exists in the canonical graph."
            )

        # Every proposed edge must reference an existing
        # canonical node or a node proposed in this suggestion.
        valid_node_ids = canonical_node_ids | set(proposed_node_ids)

        for edge in suggestion.proposed_edges:

            if (
                edge.source_id not in valid_node_ids
                or edge.target_id not in valid_node_ids
            ):
                raise ValueError(f"Invalid graph reference in edge: {edge.id}")

            if edge.source_id == edge.target_id:
                raise ValueError(f"Self-referencing edge is not allowed: {edge.id}")

    def _update_suggestion_status(
        self,
        suggestion: StorySuggestion,
        status: str,
        note: str,
    ) -> SuggestionGraph:
        """
        Return an updated suggestion graph.
        """

        updated = suggestion.model_copy(
            update={
                "status": status,
                "approval_note": note,
            }
        )

        updated_suggestions = [
            updated if item.suggestion_id == suggestion.suggestion_id else item
            for item in self.suggestion_graph.suggestions
        ]

        return self.suggestion_graph.model_copy(
            update={"suggestions": updated_suggestions}
        )

    def approve_suggestion(
        self,
        suggestion_id: str,
        override_warnings: bool = False,
        override_reason: str | None = None,
    ) -> SuggestionApprovalResult:
        """
        Approve a suggestion and apply its proposed
        nodes and edges to a new canonical graph version.
        """

        suggestion = self.get_suggestion(suggestion_id)

        if suggestion.status != "proposed":
            raise ValueError("Only proposed suggestions can be approved.")

        # Separate critical problems from warnings.
        critical_findings = [
            finding
            for finding in suggestion.guardrail_findings
            if finding.severity == "critical"
        ]

        warnings = [
            finding
            for finding in suggestion.guardrail_findings
            if finding.severity == "warning"
        ]

        # Critical problems cannot be overridden.
        if critical_findings:
            raise ValueError("Cannot approve a suggestion with critical findings.")

        # Warnings require explicit author permission.
        if warnings and not override_warnings:
            raise ValueError("Warning findings require explicit author override.")

        if warnings and not (override_reason or "").strip():
            raise ValueError("An override reason is required.")

        # Check that all proposed graph changes are valid.
        self._validate_changes(suggestion)

        # Create a NEW canonical graph.
        new_canonical_graph = self.canonical_graph.model_copy(
            update={
                "nodes": [
                    *self.canonical_graph.nodes,
                    *suggestion.proposed_nodes,
                ],
                "edges": [
                    *self.canonical_graph.edges,
                    *suggestion.proposed_edges,
                ],
                "approval_status": "approved",
            }
        )

        # Record the author's decision.
        approval_note = override_reason.strip() if warnings else "Approved by author."

        # Update the suggestion status.
        new_suggestion_graph = self._update_suggestion_status(
            suggestion,
            "approved",
            approval_note,
        )

        # Update manager state only after all checks pass.
        self.canonical_graph = new_canonical_graph
        self.suggestion_graph = new_suggestion_graph

        return SuggestionApprovalResult(
            action="approved",
            message=(
                "Suggestion approved and applied " "to a new canonical graph version."
            ),
            canonical_graph=new_canonical_graph,
            suggestion_graph=new_suggestion_graph,
        )

    def reject_suggestion(
        self,
        suggestion_id: str,
        reason: str = "",
    ) -> SuggestionApprovalResult:
        """
        Reject a suggestion without modifying the
        canonical knowledge graph.
        """

        suggestion = self.get_suggestion(suggestion_id)

        if suggestion.status != "proposed":
            raise ValueError("Only proposed suggestions can be rejected.")

        rejection_note = reason.strip() if reason.strip() else "Rejected by author."

        # Update only the suggestion graph.
        new_suggestion_graph = self._update_suggestion_status(
            suggestion,
            "rejected",
            rejection_note,
        )

        self.suggestion_graph = new_suggestion_graph

        return SuggestionApprovalResult(
            action="rejected",
            message=("Suggestion rejected. " "Canonical graph remains unchanged."),
            canonical_graph=self.canonical_graph,
            suggestion_graph=new_suggestion_graph,
        )
