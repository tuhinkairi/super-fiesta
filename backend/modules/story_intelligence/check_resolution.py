from modules.story_intelligence.models.character import (
    Character,
    CharacterExtractionResult,
)

from modules.story_intelligence.knowledge_graph.entity_resolver import (
    EntityResolver,
)


def main():

    # Simulate duplicate records extracted from different passages.
    characters = CharacterExtractionResult(
        characters=[
            Character(
                name="Arjun",
                role_in_story="Main character",
                personality_traits=["brave"],
            ),
            Character(
                name="Inspector Arjun",
                aliases=["Arjun"],
                role_in_story="Police inspector",
                personality_traits=["determined"],
            ),
            Character(
                name="Maya",
                role_in_story="Arjun's sister",
            ),
        ]
    )

    resolver = EntityResolver()

    result = resolver.resolve(characters)

    print("Entity resolution successful!")

    print("\nResolved characters:\n")

    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
