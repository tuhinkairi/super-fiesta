from modules.story_intelligence.models.graph import (
    GraphNode,
    StoryKnowledgeGraph,
)

from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
    SuggestionGraph,
)

from modules.story_intelligence.suggestion_graph.suggestion_builder import (
    SuggestionBuilder,
)


def main():

    # Create an approved canonical graph.
    canonical_graph = StoryKnowledgeGraph(
        project_id="test-project-001",
        nodes=[
            GraphNode(
                id="arjun",
                node_type="character",
                label="Arjun",
            ),
            GraphNode(
                id="maya",
                node_type="character",
                label="Maya",
            ),
        ],
        edges=[],
        approval_status="approved",
    )

    # Record original graph size.
    original_node_count = len(canonical_graph.nodes)
    original_edge_count = len(canonical_graph.edges)

    # Initialize the suggestion builder.
    builder = SuggestionBuilder(canonical_graph)

    # Create a hypothetical story idea.
    suggestion = StorySuggestion(
        title="Maya's secret alliance",
        description=(
            "Maya may secretly be cooperating with " "the enemy to protect Arjun."
        ),
        suggestion_type="plot_twist",
        rationale=("This introduces a potential moral conflict."),
        based_on_node_ids=["arjun", "maya"],
    )

    # Add the suggestion.
    result = builder.add_suggestion(suggestion)

    # Retrieve it.
    retrieved = builder.get_suggestion(suggestion.suggestion_id)

    # Check the status.
    print("Suggestion graph built successfully!")

    print("\nProject ID:", result.project_id)

    print(
        "Number of suggestions:",
        len(result.suggestions),
    )

    print(
        "Suggestion status:",
        retrieved.status,
    )

    # Confirm canonical graph remains unchanged.
    print(
        "\nCanonical node count unchanged:",
        len(canonical_graph.nodes) == original_node_count,
    )

    print(
        "Canonical edge count unchanged:",
        len(canonical_graph.edges) == original_edge_count,
    )

    print("\nSuggestion JSON:\n")

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
