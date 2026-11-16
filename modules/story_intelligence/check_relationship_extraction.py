
from modules.story_intelligence.models.character import (
    Character,
    CharacterExtractionResult,
)

from modules.story_intelligence.knowledge_graph.relation_extractor import (
    RelationExtractor,
)


story = """
Arjun entered the palace.
His sister Maya was waiting for him.
She revealed that Rohan, his closest friend,
had secretly joined the enemy.
"""


def main():

    # These are example character records.
    # In our complete pipeline, they will come from
    # the character extraction and entity resolution stages.

    characters = CharacterExtractionResult(
        characters=[
            Character(name="Arjun"),
            Character(name="Maya"),
            Character(name="Rohan"),
        ]
    )

    extractor = RelationExtractor()

    try:
        print("Analyzing character relationships...")

        result = extractor.extract_relationships(
            story_text=story,
            characters=characters,
        )

        print("\nRelationship extraction successful!")

        print("\nExtracted relationships:\n")

        print(result.model_dump_json(indent=2))

    except Exception as error:
        print("\nRelationship extraction failed:")
        print(error)

    finally:
        extractor.close()


if __name__ == "__main__":
    main()
