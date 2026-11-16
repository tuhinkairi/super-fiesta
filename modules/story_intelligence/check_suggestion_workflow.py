
from modules.story_intelligence.models.graph import (
    GraphNode,
    StoryKnowledgeGraph,
)
from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
)
from modules.story_intelligence.suggestion_graph.suggestion_workflow import (
    SuggestionWorkflow,
)


class FakeLLMClient:
    """Simulates Gemini without making an API request."""

    def __init__(self, result):
        self.result = result
        self.called = False

    def generate_structured(self, prompt, response_schema):
        self.called = True

        assert response_schema == SuggestionGraph
        assert "CANONICAL STORY KNOWLEDGE GRAPH" in prompt
        assert "ADDITIONAL STORY CONTEXT" in prompt

        return self.result


def make_canonical_graph():
    """Create an approved canonical story graph."""

    return StoryKnowledgeGraph(
        project_id="workflow_test_project",
        nodes=[
            GraphNode(
                id="character_arjun",
                node_type="character",
                label="Arjun",
                properties={},
            )
        ],
        edges=[],
        approval_status="approved",
        validation_warnings=[],
    )


def make_suggestion(
    suggestion_id,
    proposed_node_id,
    title,
):
    """Create a hypothetical suggestion for testing."""

    return StorySuggestion(
        suggestion_id=suggestion_id,
        title=title,
        description="A possible new story development.",
        suggestion_type="new_event",
        rationale="This creates an additional story possibility.",
        based_on_node_ids=["character_arjun"],
        source_evidence=[
            "Arjun is an established character in the story."
        ],
        proposed_nodes=[
            GraphNode(
                id=proposed_node_id,
                node_type="event",
                label=title,
                properties={},
            )
        ],
        proposed_edges=[],
        guardrail_findings=[],
        status="proposed",
        approval_note="",
    )


def make_generated_result():
    """Prepare fake suggestions returned by Gemini."""

    return SuggestionGraph(
        project_id="workflow_test_project",
        suggestions=[
            make_suggestion(
                suggestion_id="suggestion_approve",
                proposed_node_id="event_approved",
                title="Arjun discovers a hidden letter",
            ),
            make_suggestion(
                suggestion_id="suggestion_reject",
                proposed_node_id="event_rejected",
                title="Arjun meets a mysterious stranger",
            ),
        ],
    )


def test_complete_suggestion_workflow():
    """Test generation, validation, approval and rejection."""

    original_graph = make_canonical_graph()
    fake_client = FakeLLMClient(make_generated_result())

    workflow = SuggestionWorkflow(
        canonical_graph=original_graph,
        llm_client=fake_client,
    )

    # --------------------------------------------------
    # 1. Generate and validate suggestions.
    # --------------------------------------------------

    suggestion_graph = workflow.generate_suggestions(
        story_context=(
            "Arjun is investigating a mystery "
            "in his hometown."
        ),
        max_suggestions=2,
    )

    assert fake_client.called
    assert suggestion_graph.project_id == "workflow_test_project"
    assert len(suggestion_graph.suggestions) == 2

    assert all(
        suggestion.status == "proposed"
        for suggestion in suggestion_graph.suggestions
    )

    print("PASS: Suggestions generated successfully.")
    print("PASS: Suggestions passed through guardrail validation.")

    # --------------------------------------------------
    # 2. Approve the first suggestion.
    # --------------------------------------------------

    approval_result = workflow.approve_suggestion(
        suggestion_id="suggestion_approve"
    )

    assert approval_result.action == "approved"

    approved_suggestion = workflow.get_suggestion(
        "suggestion_approve"
    )

    assert approved_suggestion.status == "approved"

    approved_node_ids = {
        node.id for node in workflow.canonical_graph.nodes
    }

    assert "event_approved" in approved_node_ids

    print("PASS: Suggestion approved.")
    print("PASS: Approved changes added to the canonical graph.")

    # --------------------------------------------------
    # 3. Reject the second suggestion.
    # --------------------------------------------------

    node_count_before_rejection = len(
        workflow.canonical_graph.nodes
    )

    rejection_result = workflow.reject_suggestion(
        suggestion_id="suggestion_reject",
        reason="This development does not fit the current story.",
    )

    assert rejection_result.action == "rejected"

    rejected_suggestion = workflow.get_suggestion(
        "suggestion_reject"
    )

    assert rejected_suggestion.status == "rejected"

    assert len(workflow.canonical_graph.nodes) == (
        node_count_before_rejection
    )

    rejected_node_ids = {
        node.id for node in workflow.canonical_graph.nodes
    }

    assert "event_rejected" not in rejected_node_ids

    print("PASS: Suggestion rejected.")
    print("PASS: Rejection did not modify the canonical graph.")

    # --------------------------------------------------
    # 4. Verify original graph was never mutated.
    # --------------------------------------------------

    assert len(original_graph.nodes) == 1
    assert "event_approved" not in {
        node.id for node in original_graph.nodes
    }

    assert "event_rejected" not in {
        node.id for node in original_graph.nodes
    }

    print("PASS: Original canonical graph remains unchanged.")

    # --------------------------------------------------
    # 5. Verify final suggestion statuses.
    # --------------------------------------------------

    assert len(workflow.list_suggestions()) == 2
    assert len(workflow.list_suggestions("approved")) == 1
    assert len(workflow.list_suggestions("rejected")) == 1
    assert len(workflow.list_suggestions("proposed")) == 0

    print("PASS: Suggestion statuses are correct.")

    workflow.close()

    print("\nALL SUGGESTION WORKFLOW CHECKS PASSED!")


if __name__ == "__main__":
    test_complete_suggestion_workflow()
