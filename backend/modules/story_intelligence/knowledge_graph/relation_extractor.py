import json
from pathlib import Path

from modules.story_intelligence.llm.llm_client import LLMClient

from modules.story_intelligence.models.character import (
    CharacterExtractionResult,
)

from modules.story_intelligence.models.relationship import (
    RelationshipExtractionResult,
)


class RelationExtractor:
    """
    Extracts relationships between previously identified
    characters using Gemini.

    Supports dependency injection for shared LLM clients.
    """

    def __init__(self, llm_client: LLMClient | None = None):

        # Track whether this extractor owns the client.
        self._owns_client = llm_client is None

        # Use shared client or create a new client.
        self.llm_client = llm_client if llm_client is not None else LLMClient()

        # Locate relationship extraction prompt.
        self.prompt_path = (
            Path(__file__).resolve().parent.parent
            / "llm"
            / "prompts"
            / "relation_extraction.txt"
        )

    def _load_prompt(self) -> str:
        """
        Load relationship extraction instructions.
        """

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Relationship extraction prompt not found: " f"{self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8")

    @staticmethod
    def _normalize_name(name: str) -> str:
        """
        Normalize a character name for comparison.
        """

        return " ".join(name.casefold().split())

    def _build_character_lookup(
        self,
        characters: CharacterExtractionResult,
    ) -> dict[str, str]:
        """
        Map canonical names and unambiguous aliases
        to their canonical character names.
        """

        lookup = {}
        ambiguous = set()

        for character in characters.characters:

            identifiers = [
                character.name,
                *character.aliases,
            ]

            for identifier in identifiers:

                key = self._normalize_name(identifier)

                if not key:
                    continue

                existing = lookup.get(key)

                if existing is not None and existing != character.name:
                    ambiguous.add(key)
                else:
                    lookup[key] = character.name

        # Never automatically resolve ambiguous identifiers.
        for key in ambiguous:
            lookup.pop(key, None)

        return lookup

    def extract_relationships(
        self,
        story_text: str,
        characters: CharacterExtractionResult,
    ) -> RelationshipExtractionResult:
        """
        Extract character relationships from story text.
        """

        if not story_text or not story_text.strip():
            raise ValueError("Story text cannot be empty.")

        # No characters means no character relationships.
        if not characters.characters:
            return RelationshipExtractionResult(relationships=[])

        # Prepare canonical names and aliases.
        character_data = [
            {
                "name": character.name,
                "aliases": character.aliases,
            }
            for character in characters.characters
        ]

        character_json = json.dumps(
            character_data,
            ensure_ascii=False,
            indent=2,
        )

        # Load relationship instructions.
        prompt_template = self._load_prompt()

        # Check prompt placeholders.
        required_placeholders = [
            "{characters}",
            "{story_text}",
        ]

        for placeholder in required_placeholders:
            if placeholder not in prompt_template:
                raise ValueError(
                    f"Relationship prompt is missing " f"the {placeholder} placeholder."
                )

        # Insert characters and original story text.
        prompt = prompt_template.replace(
            "{characters}",
            character_json,
        ).replace(
            "{story_text}",
            story_text.strip(),
        )

        # Request structured relationship information.
        result = self.llm_client.generate_structured(
            prompt=prompt,
            response_schema=RelationshipExtractionResult,
        )

        # Map canonical names and aliases.
        character_lookup = self._build_character_lookup(characters)

        validated_relationships = []

        for relationship in result.relationships:

            source_key = self._normalize_name(relationship.source_character)

            target_key = self._normalize_name(relationship.target_character)

            source_name = character_lookup.get(source_key)
            target_name = character_lookup.get(target_key)

            # Reject references to unknown or ambiguous characters.
            if source_name is None:
                raise ValueError(
                    f"Unknown or ambiguous source character: "
                    f"{relationship.source_character}"
                )

            if target_name is None:
                raise ValueError(
                    f"Unknown or ambiguous target character: "
                    f"{relationship.target_character}"
                )

            # A character cannot have a relationship with itself.
            if source_name == target_name:
                raise ValueError(f"Invalid self-relationship: {source_name}")

            # Standardize names to canonical character names.
            validated_relationships.append(
                relationship.model_copy(
                    update={
                        "source_character": source_name,
                        "target_character": target_name,
                    }
                )
            )

        return RelationshipExtractionResult(relationships=validated_relationships)

    def close(self) -> None:
        """
        Close the client only if this extractor created it.
        """

        if self._owns_client:
            self.llm_client.close()
