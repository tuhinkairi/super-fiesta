
from modules.story_intelligence.knowledge_graph.entity_extractor import (
    EntityExtractor
)

story = """
Arjun entered the palace.
His sister Maya was waiting for him.
She revealed that Rohan, his closest friend,
had secretly joined the enemy.
"""


def main():
    extractor = EntityExtractor()

    try:
        print("Analyzing story...")

        result = extractor.extract_characters(story)

        print("\nCharacter extraction successful!")
        print("\nExtracted characters:\n")

        print(result.model_dump_json(indent=2))

    except Exception as error:
        print("\nCharacter extraction failed:")
        print(error)

    finally:
        extractor.close()


if __name__ == "__main__":
    main()
