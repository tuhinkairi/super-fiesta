from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)

from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
    SuggestionFinding,
)

from modules.story_intelligence.suggestion_graph.approval_manager import (
    ApprovalManager,
)


def main():

    # -----------------------------------------
    # 1. Create the approved canonical graph.
    # -----------------------------------------

    canonical_graph = StoryKnowledgeGraph(
        project_id="approval-test-project",
        nodes=[
            GraphNode(
                id="arjun",
                node_type="character",
                label="Arjun",
            ),
            GraphNode(
                id="rohan",
                node_type="character",
                label="Rohan",
            ),
        ],
        edges=[],
        approval_status="approved",
    )

    original_node_count = len(canonical_graph.nodes)
    original_edge_count = len(canonical_graph.edges)

    # -----------------------------------------
    # 2. Create a suggestion that can be approved.
    # -----------------------------------------

    approved_idea = StorySuggestion(
        title="Rohan joins the enemy",
        description=("Rohan secretly joins the enemy faction."),
        suggestion_type="plot_twist",
        rationale=("This could introduce a major conflict."),
        based_on_node_ids=[
            "arjun",
            "rohan",
        ],
        source_evidence=["Rohan is Arjun's closest friend."],
        proposed_nodes=[
            GraphNode(
                id="event_rohan_enemy",
                node_type="event",
                label="Rohan joins the enemy",
            )
        ],
        proposed_edges=[
            GraphEdge(
                id="edge_rohan_enemy",
                source_id="rohan",
                target_id="event_rohan_enemy",
                edge_type="PARTICIPATED_IN",
            )
        ],
    )

    # -----------------------------------------
    # 3. Create a suggestion that will be rejected.
    # -----------------------------------------

    rejected_idea = StorySuggestion(
        title="Arjun loses his memory",
        description=("Arjun unexpectedly loses his memory."),
        suggestion_type="character_development",
        based_on_node_ids=[
            "arjun",
        ],
    )

    # -----------------------------------------
    # 4. Create the suggestion graph.
    # -----------------------------------------

    suggestion_graph = SuggestionGraph(
        project_id="approval-test-project",
        suggestions=[
            approved_idea,
            rejected_idea,
        ],
    )

    # -----------------------------------------
    # 5. Initialize approval manager.
    # -----------------------------------------

    manager = ApprovalManager(
        canonical_graph=canonical_graph,
        suggestion_graph=suggestion_graph,
    )

    # -----------------------------------------
    # 6. Approve the first suggestion.
    # -----------------------------------------

    approved_result = manager.approve_suggestion(approved_idea.suggestion_id)

    print("Approval decision:", approved_result.action)

    print(
        "Approved suggestion status:",
        manager.get_suggestion(approved_idea.suggestion_id).status,
    )

    print(
        "Canonical nodes after approval:",
        len(approved_result.canonical_graph.nodes),
    )

    print(
        "Canonical edges after approval:",
        len(approved_result.canonical_graph.edges),
    )

    # -----------------------------------------
    # 7. Reject the second suggestion.
    # -----------------------------------------

    node_count_before_rejection = len(manager.canonical_graph.nodes)

    rejected_result = manager.reject_suggestion(
        rejected_idea.suggestion_id,
        reason="This direction does not fit the story.",
    )

    print("\nRejection decision:", rejected_result.action)

    print(
        "Rejected suggestion status:",
        manager.get_suggestion(rejected_idea.suggestion_id).status,
    )

    # -----------------------------------------
    # 8. Verify graph integrity.
    # -----------------------------------------

    print(
        "\nCanonical graph preserved after rejection:",
        len(manager.canonical_graph.nodes) == node_count_before_rejection,
    )

    print(
        "Original graph was not mutated:",
        len(canonical_graph.nodes) == original_node_count
        and len(canonical_graph.edges) == original_edge_count,
    )

    print(
        "Suggestion graph contains both decisions:",
        len(manager.suggestion_graph.suggestions) == 2,
    )

    # -----------------------------------------
    # 9. Test warning override protection.
    # -----------------------------------------

    warning_idea = StorySuggestion(
        title="Rohan betrays Arjun",
        description="Rohan becomes Arjun's enemy.",
        suggestion_type="relationship_change",
        based_on_node_ids=["arjun", "rohan"],
        guardrail_findings=[
            SuggestionFinding(
                rule_id="CONFLICTING_RELATIONSHIP",
                severity="warning",
                message="This conflicts with an existing relationship.",
                involved_node_ids=["arjun", "rohan"],
            )
        ],
    )

    # Add warning suggestion to the suggestion graph.
    manager.suggestion_graph = manager.suggestion_graph.model_copy(
        update={
            "suggestions": [
                *manager.suggestion_graph.suggestions,
                warning_idea,
            ]
        }
    )

    try:
        manager.approve_suggestion(warning_idea.suggestion_id)
    except ValueError as error:
        print("\nWarning protection working:", error)

    # Explicit author override.
    override_result = manager.approve_suggestion(
        warning_idea.suggestion_id,
        override_warnings=True,
        override_reason=(
            "Author intentionally wants this relationship "
            "to change later in the story."
        ),
    )

    print(
        "Warning override decision:",
        override_result.action,
    )

    print("\nApproval manager test completed successfully!")


if __name__ == "__main__":
    main()
