
from modules.story_intelligence.models.graph import StoryKnowledgeGraph
from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
)


class SuggestionBuilder:
    """
    Manages hypothetical story suggestions separately
    from the canonical knowledge graph.
    """

    def __init__(
        self,
        canonical_graph: StoryKnowledgeGraph,
        suggestion_graph: SuggestionGraph | None = None,
    ):
        # Suggestions must be based on author-approved facts.
        if canonical_graph.approval_status != "approved":
            raise ValueError(
                "Canonical graph must be approved before "
                "building story suggestions."
            )

        self.canonical_graph = canonical_graph

        if suggestion_graph is None:
            suggestion_graph = SuggestionGraph(
                project_id=canonical_graph.project_id,
                suggestions=[],
            )

        if suggestion_graph.project_id != canonical_graph.project_id:
            raise ValueError(
                "Canonical and suggestion graph project IDs "
                "must match."
            )

        self.suggestion_graph = suggestion_graph

    def _validate_suggestion(
        self,
        suggestion: StorySuggestion,
    ) -> None:
        """Validate a suggestion before adding it."""

        if suggestion.status != "proposed":
            raise ValueError(
                "New suggestions must have proposed status."
            )

        canonical_node_ids = {
            node.id for node in self.canonical_graph.nodes
        }

        # Validate canonical references.
        for node_id in suggestion.based_on_node_ids:
            if node_id not in canonical_node_ids:
                raise ValueError(
                    f"Unknown canonical node reference: {node_id}"
                )

        # Prevent duplicate suggestion IDs.
        existing_suggestion_ids = {
            item.suggestion_id
            for item in self.suggestion_graph.suggestions
        }

        if suggestion.suggestion_id in existing_suggestion_ids:
            raise ValueError("Suggestion ID already exists.")

        # Validate proposed node IDs.
        proposed_node_ids = [
            node.id for node in suggestion.proposed_nodes
        ]

        if len(proposed_node_ids) != len(set(proposed_node_ids)):
            raise ValueError("Duplicate proposed node IDs found.")

        if set(proposed_node_ids) & canonical_node_ids:
            raise ValueError(
                "Proposed node IDs cannot overwrite canonical nodes."
            )

        existing_node_ids = {
            node.id
            for item in self.suggestion_graph.suggestions
            for node in item.proposed_nodes
        }

        if existing_node_ids & set(proposed_node_ids):
            raise ValueError(
                "Proposed node ID already exists in suggestion graph."
            )

        # Validate proposed edge IDs.
        proposed_edge_ids = [
            edge.id for edge in suggestion.proposed_edges
        ]

        if len(proposed_edge_ids) != len(set(proposed_edge_ids)):
            raise ValueError("Duplicate proposed edge IDs found.")

        canonical_edge_ids = {
            edge.id for edge in self.canonical_graph.edges
        }

        if canonical_edge_ids & set(proposed_edge_ids):
            raise ValueError(
                "Proposed edge IDs cannot overwrite canonical edges."
            )

        existing_edge_ids = {
            edge.id
            for item in self.suggestion_graph.suggestions
            for edge in item.proposed_edges
        }

        if existing_edge_ids & set(proposed_edge_ids):
            raise ValueError(
                "Proposed edge ID already exists in suggestion graph."
            )

        # Validate edge endpoints.
        valid_node_ids = canonical_node_ids | set(proposed_node_ids)

        for edge in suggestion.proposed_edges:
            if (
                edge.source_id not in valid_node_ids
                or edge.target_id not in valid_node_ids
            ):
                raise ValueError(
                    f"Suggestion edge {edge.id} references "
                    "an unknown node."
                )

    def add_suggestion(
        self,
        suggestion: StorySuggestion,
    ) -> SuggestionGraph:
        """Validate and add a hypothetical story suggestion."""

        self._validate_suggestion(suggestion)

        updated_suggestions = [
            *self.suggestion_graph.suggestions,
            suggestion,
        ]

        self.suggestion_graph = SuggestionGraph(
            project_id=self.suggestion_graph.project_id,
            suggestions=updated_suggestions,
        )

        return self.suggestion_graph

    def get_suggestion(
        self,
        suggestion_id: str,
    ) -> StorySuggestion | None:
        """Retrieve a suggestion using its suggestion_id."""

        for suggestion in self.suggestion_graph.suggestions:
            if suggestion.suggestion_id == suggestion_id:
                return suggestion

        return None

    def list_suggestions(
        self,
        status: str | None = None,
    ) -> list[StorySuggestion]:
        """Return all suggestions or filter by status."""

        if status is None:
            return list(self.suggestion_graph.suggestions)

        return [
            suggestion
            for suggestion in self.suggestion_graph.suggestions
            if suggestion.status == status
        ]
