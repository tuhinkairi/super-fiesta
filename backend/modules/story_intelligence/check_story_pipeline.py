from modules.story_intelligence.pipeline.orchestrator import (
    StoryOrchestrator,
)

from modules.story_intelligence.types import StoryInput

from modules.story_intelligence.models.character import (
    Character,
    CharacterExtractionResult,
    CharacterEvidence,
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
    Simulates Gemini responses without making API requests.
    """

    def generate_structured(self, prompt, response_schema):

        print("\nMock Gemini response generated.")

        if response_schema == CharacterExtractionResult:

            return CharacterExtractionResult(
                characters=[
                    Character(
                        name="Arjun",
                    ),
                    Character(
                        name="Maya",
                        evidence=[
                            CharacterEvidence(
                                fact="Maya is Arjun's sister.",
                                quote=("His sister Maya was waiting for him."),
                                evidence_type="explicit",
                            )
                        ],
                    ),
                    Character(
                        name="Rohan",
                    ),
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
                                quote=("His sister Maya was waiting for him."),
                                evidence_type="explicit",
                            )
                        ],
                    ),
                    CharacterRelationship(
                        source_character="Rohan",
                        target_character="Arjun",
                        relationship_type="FRIEND_OF",
                        description=("Rohan is Arjun's closest friend."),
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
                        description=("Maya reveals Rohan's allegiance."),
                        participants=["Maya", "Rohan"],
                        location="Palace",
                        chapter_number=1,
                        sequence_index=2,
                        chronology_basis="narrative_order",
                        evidence=[
                            EventEvidence(
                                quote=(
                                    "She revealed that Rohan, "
                                    "his closest friend, had "
                                    "secretly joined the enemy."
                                ),
                                evidence_type="explicit",
                            )
                        ],
                    ),
                ]
            )

        raise ValueError(f"Unexpected response schema: {response_schema}")


def main():

    story = """
    Arjun entered the palace.
    His sister Maya was waiting for him.
    She revealed that Rohan, his closest friend,
    had secretly joined the enemy.
    """

    # Create the input.
    story_input = StoryInput(
        project_id="unified-test-project",
        story_text=story,
        chapter_number=1,
    )

    # Inject mock Gemini client.
    fake_client = FakeLLMClient()

    orchestrator = StoryOrchestrator(llm_client=fake_client)

    try:

        print("Starting complete Story Intelligence pipeline...")

        result = orchestrator.process_story(story_input)

        print("\n" + "=" * 50)
        print("STORY PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 50)

        print("\nProject ID:", result.project_id)

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
            "Timeline events:",
            len(result.timeline.events),
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
            "Graph approval status:",
            result.knowledge_graph.approval_status,
        )

        print("\nExtracted characters:")

        for character in result.characters.characters:
            print("-", character.name)

        print("\nStory relationships:")

        for relationship in result.relationships.relationships:
            print(
                relationship.source_character,
                relationship.relationship_type,
                relationship.target_character,
            )

        print("\nTimeline:")

        for event in result.timeline.events:
            print(f"Chapter {event.chapter_number}: " f"{event.title}")

        print("\nFinal result JSON:")

        print(result.model_dump_json(indent=2))

    finally:
        orchestrator.close()


if __name__ == "__main__":
    main()
