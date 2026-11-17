from modules.story_intelligence.models.graph import (
    GraphNode,
    StoryKnowledgeGraph,
)
from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
)
from modules.story_intelligence.suggestion_graph.suggestion_generator import (
    SuggestionGenerator,
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


def make_graph(approval_status="approved"):
    return StoryKnowledgeGraph(
        project_id="demo_project",
        nodes=[
            GraphNode(
                id="character_arjun",
                node_type="character",
                label="Arjun",
                properties={},
            )
        ],
        edges=[],
        approval_status=approval_status,
        validation_warnings=[],
    )


def make_suggestion_result(
    based_on_node_ids=None,
    status="proposed",
):
    if based_on_node_ids is None:
        based_on_node_ids = ["character_arjun"]

    suggestion = StorySuggestion(
        suggestion_id="suggestion_1",
        title="Arjun faces a difficult choice",
        description="Arjun must decide whether to reveal a secret.",
        suggestion_type="character_development",
        rationale="This could create a meaningful character conflict.",
        based_on_node_ids=based_on_node_ids,
        source_evidence=["Arjun has been hiding an important secret."],
        proposed_nodes=[],
        proposed_edges=[],
        guardrail_findings=[],
        status=status,
        approval_note="",
    )

    return SuggestionGraph(
        project_id="demo_project",
        suggestions=[suggestion],
    )


def test_successful_generation():
    graph = make_graph()
    fake_client = FakeLLMClient(make_suggestion_result())

    generator = SuggestionGenerator(llm_client=fake_client)

    result = generator.generate_suggestions(
        canonical_graph=graph,
        story_context=("Arjun is hiding a secret from his closest friend."),
        max_suggestions=2,
    )

    assert fake_client.called
    assert result.project_id == "demo_project"
    assert len(result.suggestions) == 1

    suggestion = result.suggestions[0]

    assert suggestion.status == "proposed"
    assert suggestion.suggestion_id == "suggestion_1"

    # The canonical graph must remain unchanged.
    assert len(graph.nodes) == 1
    assert len(graph.edges) == 0

    generator.close()

    print("PASS: Suggestion generation works.")
    print("PASS: Generated suggestions remain proposed.")
    print("PASS: Canonical graph remains unchanged.")


def test_unapproved_graph_rejected():
    graph = make_graph(approval_status="pending")
    fake_client = FakeLLMClient(make_suggestion_result())

    generator = SuggestionGenerator(llm_client=fake_client)

    try:
        generator.generate_suggestions(
            canonical_graph=graph,
            story_context="Test story",
        )
        raise AssertionError("Expected ValueError was not raised.")

    except ValueError as error:
        assert "approved canonical graph" in str(error)

    assert not fake_client.called

    generator.close()

    print("PASS: Unapproved graph is rejected.")


def test_unknown_node_reference_rejected():
    graph = make_graph()

    invalid_result = make_suggestion_result(
        based_on_node_ids=["character_does_not_exist"]
    )

    fake_client = FakeLLMClient(invalid_result)
    generator = SuggestionGenerator(llm_client=fake_client)

    try:
        generator.generate_suggestions(
            canonical_graph=graph,
            story_context="Test story",
        )
        raise AssertionError("Expected ValueError was not raised.")

    except ValueError as error:
        assert "unknown canonical nodes" in str(error)

    generator.close()

    print("PASS: Unknown canonical node references are rejected.")


def run_tests():
    test_successful_generation()
    test_unapproved_graph_rejected()
    test_unknown_node_reference_rejected()

    print("\nAll suggestion generator checks passed!")


if __name__ == "__main__":
    run_tests()
