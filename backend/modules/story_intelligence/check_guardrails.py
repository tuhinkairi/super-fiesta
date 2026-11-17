from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)

from modules.story_intelligence.models.suggestion import (
    StorySuggestion,
)

from modules.story_intelligence.suggestion_graph.guardrail_engine import (
    GuardrailEngine,
)


def main():

    # ---------------------------------------------
    # 1. Create the canonical story graph.
    # ---------------------------------------------

    canonical_graph = StoryKnowledgeGraph(
        project_id="test-project-001",
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
        edges=[
            GraphEdge(
                id="relationship_1",
                source_id="rohan",
                target_id="arjun",
                edge_type="FRIEND_OF",
                directed=False,
                confidence=1.0,
                evidence=["Rohan, his closest friend."],
            )
        ],
        approval_status="approved",
    )

    # ---------------------------------------------
    # 2. Create a hypothetical suggestion.
    # ---------------------------------------------

    suggestion = StorySuggestion(
        title="Rohan becomes Arjun's enemy",
        description=("Rohan secretly begins working against Arjun."),
        suggestion_type="relationship_change",
        rationale=("This could create a major conflict."),
        based_on_node_ids=[
            "arjun",
            "rohan",
        ],
        source_evidence=["Rohan, his closest friend."],
        proposed_edges=[
            GraphEdge(
                id="suggested_relationship_1",
                source_id="rohan",
                target_id="arjun",
                edge_type="ENEMY_OF",
                directed=False,
                confidence=0.8,
                evidence=["Rohan secretly begins working against Arjun."],
            )
        ],
    )

    # ---------------------------------------------
    # 3. Run the Guardrail Engine.
    # ---------------------------------------------

    engine = GuardrailEngine(canonical_graph)

    validated_suggestion = engine.validate(suggestion)

    # ---------------------------------------------
    # 4. Display validation findings.
    # ---------------------------------------------

    print("Guardrail validation completed!")

    print("\nSuggestion:", validated_suggestion.title)

    print(
        "\nNumber of findings:",
        len(validated_suggestion.guardrail_findings),
    )

    for finding in validated_suggestion.guardrail_findings:

        print("\nRule:", finding.rule_id)
        print("Severity:", finding.severity)
        print("Message:", finding.message)

    # ---------------------------------------------
    # 5. Verify that the original graph is unchanged.
    # ---------------------------------------------

    print(
        "\nCanonical graph unchanged:",
        canonical_graph.edges[0].edge_type == "FRIEND_OF",
    )

    print(
        "Suggestion remains proposed:",
        validated_suggestion.status == "proposed",
    )


if __name__ == "__main__":
    main()
