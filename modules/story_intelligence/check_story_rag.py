
from modules.story_intelligence.story_rag import StoryRAG
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


class FakeLLMClient:
    """
    Simulates Gemini responses for testing.
    """

    def __init__(self):

        self.call_count = 0

    def generate_structured(self, prompt, response_schema):

        self.call_count += 1

        if response_schema == CharacterExtractionResult:

            return CharacterExtractionResult(
                characters=[
                    Character(name="Arjun"),
                    Character(name="Maya"),
                    Character(name="Rohan"),
                ]
            )

        if response_schema == RelationshipExtractionResult:

            return RelationshipExtractionResult(
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

        if response_schema == EventExtractionResult:

            return EventExtractionResult(
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
                                quote=(
                                    "She revealed that Rohan had "
                                    "secretly joined the enemy."
                                ),
                                evidence_type="explicit",
                            )
                        ],
                    ),
                ]
            )

        raise ValueError(
            f"Unexpected response schema: {response_schema}"
        )


def main():

    story = """
    Arjun entered the palace.
    His sister Maya was waiting for him.
    She revealed that Rohan, his closest friend,
    had secretly joined the enemy.
    """

    fake_client = FakeLLMClient()

    # Initialize the public interface.
    story_rag = StoryRAG(
        llm_client=fake_client
    )

    try:

        print("Testing StoryRAG public interface...")

        # Process the story using one public method.
        result = story_rag.process_story(
            project_id="story-rag-test-001",
            story_text=story,
            chapter_number=1,
        )

        print("\nStoryRAG completed successfully!")

        print("\nProject:", result.project_id)

        print(
            "Characters:",
            len(result.characters.characters),
        )

        print(
            "Relationships:",
            len(result.relationships.relationships),
        )

        print(
            "Events:",
            len(result.events.events),
        )

        print(
            "Graph nodes:",
            len(result.knowledge_graph.nodes),
        )

        print(
            "Graph edges:",
            len(result.knowledge_graph.edges),
        )

        print(
            "\nGemini calls simulated:",
            fake_client.call_count,
        )

        print("\nPublic interface test passed!")

    finally:
        story_rag.close()


if __name__ == "__main__":
    main()
