
from modules.story_intelligence.models.graph import (
    GraphNode,
    GraphEdge,
    StoryKnowledgeGraph,
)

from modules.story_intelligence.knowledge_graph.graph_retriever import (
    GraphRetriever,
)


def main():

    # Create sample graph nodes.
    nodes = [
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
        GraphNode(
            id="rohan",
            node_type="character",
            label="Rohan",
        ),
        GraphNode(
            id="event_1",
            node_type="event",
            label="Arjun enters the palace",
            properties={
                "chapter_number": 1,
                "sequence_index": 1,
            },
        ),
    ]

    # Create graph edges.
    edges = [
        GraphEdge(
            id="edge_1",
            source_id="maya",
            target_id="arjun",
            edge_type="SIBLING_OF",
            directed=False,
        ),
        GraphEdge(
            id="edge_2",
            source_id="rohan",
            target_id="arjun",
            edge_type="FRIEND_OF",
            directed=False,
        ),
        GraphEdge(
            id="edge_3",
            source_id="arjun",
            target_id="event_1",
            edge_type="PARTICIPATED_IN",
        ),
    ]

    graph = StoryKnowledgeGraph(
        project_id="test-project",
        nodes=nodes,
        edges=edges,
        approval_status="approved",
    )

    # Initialize graph retrieval.
    retriever = GraphRetriever(graph)

    # Test character lookup.
    print("Character lookup:")

    character = retriever.get_character("Arjun")

    print(character.label if character else "Not found")

    # Test relationships.
    print("\nArjun's relationships:")

    relationships = retriever.get_relationships("Arjun")

    for relationship in relationships:
        print(
            relationship.edge_type,
            relationship.source_id,
            "->",
            relationship.target_id,
        )

    # Test connected characters.
    print("\nCharacters connected to Arjun:")

    related = retriever.get_related_characters("Arjun")

    for person in related:
        print(person.label)

    # Test character events.
    print("\nArjun's events:")

    events = retriever.get_events_for_character("Arjun")

    for event in events:
        print(event.label)

    print("\nGraph retrieval tests successful!")


if __name__ == "__main__":
    main()
