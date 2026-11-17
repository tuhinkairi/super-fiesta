from modules.story_intelligence.models.graph import (
    GraphNode,
    StoryKnowledgeGraph,
)
from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
)
from modules.story_intelligence.story_rag import StoryRAG


class FakeLLMClient:
    """Simulates structured Gemini responses."""

    def __init__(self):
        self.called = False

    def generate_structured(self, prompt, response_schema):
        self.called = True

        assert response_schema == SuggestionGraph
        assert "CANONICAL STORY KNOWLEDGE GRAPH" in prompt

        return SuggestionGraph(
            project_id="story_rag_suggestion_test",
            suggestions=[
                StorySuggestion(
                    suggestion_id="suggestion_approve",
                    title="Arjun discovers a hidden letter",
                    description="Arjun finds an important letter.",
                    suggestion_type="new_event",
                    rationale="This may introduce a new plot direction.",
                    based_on_node_ids=["character_arjun"],
                    source_evidence=["Arjun is investigating a mystery."],
                    proposed_nodes=[
                        GraphNode(
                            id="event_letter",
                            node_type="event",
                            label="Arjun discovers a letter",
                            properties={},
                        )
                    ],
                    proposed_edges=[],
                    guardrail_findings=[],
                    status="proposed",
                    approval_note="",
                ),
                StorySuggestion(
                    suggestion_id="suggestion_reject",
                    title="Arjun meets a stranger",
                    description="A stranger approaches Arjun.",
                    suggestion_type="new_event",
                    rationale="This introduces another possible event.",
                    based_on_node_ids=["character_arjun"],
                    source_evidence=["Arjun is investigating a mystery."],
                    proposed_nodes=[
                        GraphNode(
                            id="event_stranger",
                            node_type="event",
                            label="Arjun meets a stranger",
                            properties={},
                        )
                    ],
                    proposed_edges=[],
                    guardrail_findings=[],
                    status="proposed",
                    approval_note="",
                ),
            ],
        )


def make_approved_graph():
    """Create an author-approved canonical graph."""

    return StoryKnowledgeGraph(
        project_id="story_rag_suggestion_test",
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


def main():
    print("Testing StoryRAG suggestion interface...\n")

    original_graph = make_approved_graph()
    fake_client = FakeLLMClient()

    with StoryRAG(llm_client=fake_client) as rag:

        # 1. Initialize the suggestion workflow.
        rag.start_suggestion_workflow(original_graph)

        print("[1/5] Suggestion workflow initialized...")

        # 2. Generate suggestions.
        result = rag.generate_suggestions(
            story_context="Arjun is investigating a mystery.",
            max_suggestions=2,
        )

        assert fake_client.called
        assert len(result.suggestions) == 2

        print("[2/5] Suggestions generated successfully...")

        # 3. Retrieve and approve one suggestion.
        suggestion = rag.get_suggestion("suggestion_approve")

        assert suggestion.status == "proposed"

        approval = rag.approve_suggestion(suggestion_id=suggestion.suggestion_id)

        assert approval.action == "approved"

        assert rag.get_suggestion("suggestion_approve").status == "approved"

        assert "event_letter" in {node.id for node in rag.canonical_graph.nodes}

        print("[3/5] Suggestion approval successful...")

        # 4. Reject the other suggestion.
        rejection = rag.reject_suggestion(
            suggestion_id="suggestion_reject",
            reason="Not suitable for the current story.",
        )

        assert rejection.action == "rejected"

        assert rag.get_suggestion("suggestion_reject").status == "rejected"

        assert "event_stranger" not in {node.id for node in rag.canonical_graph.nodes}

        print("[4/5] Suggestion rejection successful...")

        # 5. Verify final state.
        assert len(rag.list_suggestions()) == 2
        assert len(rag.list_suggestions("approved")) == 1
        assert len(rag.list_suggestions("rejected")) == 1

        # The original graph must remain unchanged.
        assert len(original_graph.nodes) == 1
        assert len(original_graph.edges) == 0

        print("[5/5] Public interface and graph isolation verified...")

    print("\nSTORYRAG SUGGESTION INTERFACE TEST PASSED!")


if __name__ == "__main__":
    main()
