
from modules.story_intelligence.models.character import (
    Character,
    CharacterExtractionResult,
)

from modules.story_intelligence.models.event import (
    StoryEvent,
    EventEvidence,
    EventExtractionResult,
)

from modules.story_intelligence.knowledge_graph.event_extractor import (
    EventExtractor,
)


# Simulated Gemini response.
class FakeLLMClient:

    def generate_structured(self, prompt, response_schema):

        print("Mock AI response generated.")

        assert "{story_text}" not in prompt
        assert "{characters}" not in prompt

        return EventExtractionResult(
            events=[
                StoryEvent(
                    title="Arjun enters the palace",
                    description="Arjun enters the palace.",
                    participants=["Arjun"],
                    location="Palace",
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
                    title="Maya reveals Rohan's allegiance",
                    description="Maya reveals that Rohan joined the enemy.",
                    participants=["Maya", "Rohan"],
                    location="Palace",
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

    def close(self):
        pass


def main():

    story = """
    Arjun entered the palace.
    His sister Maya was waiting for him.
    She revealed that Rohan, his closest friend,
    had secretly joined the enemy.
    """

    characters = CharacterExtractionResult(
        characters=[
            Character(name="Arjun"),
            Character(name="Maya"),
            Character(name="Rohan"),
        ]
    )

    # Inject mock client instead of calling Gemini.
    extractor = EventExtractor(
        llm_client=FakeLLMClient()
    )

    result = extractor.extract_events(
        story_text=story,
        characters=characters,
        chapter_number=1,
    )

    print("\nEvent extraction pipeline working!")

    print("\nExtracted events:\n")

    print(result.model_dump_json(indent=2))

    extractor.close()


if __name__ == "__main__":
    main()
