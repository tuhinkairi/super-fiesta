from modules.story_intelligence.models.character import (
    Character,
    CharacterExtractionResult,
)

from modules.story_intelligence.models.relationship import (
    CharacterRelationship,
    RelationshipEvidence,
    RelationshipExtractionResult,
)

from modules.story_intelligence.models.event import (
    StoryEvent,
    EventEvidence,
    EventExtractionResult,
)

from modules.story_intelligence.knowledge_graph.graph_builder import (
    GraphBuilder,
)


def main():

    # 1. Create sample characters.
    characters = CharacterExtractionResult(
        characters=[
            Character(name="Arjun"),
            Character(name="Maya"),
            Character(name="Rohan"),
        ]
    )

    # 2. Create sample relationships.
    relationships = RelationshipExtractionResult(
        relationships=[
            CharacterRelationship(
                source_character="Maya",
                target_character="Arjun",
                relationship_type="SIBLING_OF",
                description="Maya is Arjun's sister.",
                confidence=1.0,
                evidence=[
                    RelationshipEvidence(
                        quote="His sister Maya was waiting for him.",
                        evidence_type="explicit",
                    )
                ],
            ),
            CharacterRelationship(
                source_character="Rohan",
                target_character="Arjun",
                relationship_type="FRIEND_OF",
                description="Rohan is Arjun's closest friend.",
                confidence=1.0,
                evidence=[
                    RelationshipEvidence(
                        quote="Rohan, his closest friend",
                        evidence_type="explicit",
                    )
                ],
            ),
        ]
    )

    # 3. Create sample events.
    events = EventExtractionResult(
        events=[
            StoryEvent(
                title="Arjun enters the palace",
                description="Arjun enters the palace.",
                participants=["Arjun"],
                location="Palace",
                chapter_number=1,
                sequence_index=1,
                chronology_basis="narrative_order",
                evidence=[
                    EventEvidence(
                        quote="Arjun entered the palace.",
                        evidence_type="explicit",
                    )
                ],
            ),
            StoryEvent(
                title="Maya reveals Rohan's secret",
                description="Maya reveals Rohan's allegiance.",
                participants=["Maya", "Rohan"],
                location="Palace",
                chapter_number=1,
                sequence_index=2,
                chronology_basis="narrative_order",
                evidence=[
                    EventEvidence(
                        quote="She revealed that Rohan had secretly joined the enemy.",
                        evidence_type="explicit",
                    )
                ],
            ),
        ]
    )

    # 4. Build the graph.
    graph = GraphBuilder.build(
        characters=characters,
        relationships=relationships,
        events=events,
        project_id="test-project-001",
    )

    # 5. Display the graph.
    print("Knowledge graph built successfully!")

    print("\nNumber of nodes:", len(graph.nodes))
    print("Number of edges:", len(graph.edges))

    print("\nGraph nodes:")

    for node in graph.nodes:
        print(f"{node.node_type}: {node.label} ({node.id})")

    print("\nGraph edges:")

    for edge in graph.edges:
        print(f"{edge.edge_type}: " f"{edge.source_id} -> {edge.target_id}")

    print("\nApproval status:", graph.approval_status)

    print("\nComplete graph JSON:\n")

    print(graph.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
