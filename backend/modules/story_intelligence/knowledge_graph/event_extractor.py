import json
from pathlib import Path

from modules.story_intelligence.llm.llm_client import LLMClient

from modules.story_intelligence.models.character import (
    CharacterExtractionResult,
)

from modules.story_intelligence.models.event import (
    EventExtractionResult,
)


class EventExtractor:
    """
    Extracts meaningful story events using Gemini.
    """

    def __init__(self, llm_client=None):

        # Allow mock clients during local testing.
        self._owns_client = llm_client is None

        self.llm_client = llm_client if llm_client is not None else LLMClient()

        # Locate event extraction instructions.
        self.prompt_path = (
            Path(__file__).resolve().parent.parent
            / "llm"
            / "prompts"
            / "event_extraction.txt"
        )

    def _load_prompt(self):
        """Load event extraction instructions."""

        if not self.prompt_path.exists():
            raise FileNotFoundError(f"Event prompt not found: {self.prompt_path}")

        return self.prompt_path.read_text(encoding="utf-8")

    def extract_events(
        self,
        story_text: str,
        characters: CharacterExtractionResult,
        chapter_number: int | None = None,
    ) -> EventExtractionResult:
        """Extract events from a story passage."""

        if not story_text or not story_text.strip():
            raise ValueError("Story text cannot be empty.")

        if not characters.characters:
            return EventExtractionResult(events=[])

        # Prepare known characters.
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

        # Load the extraction prompt.
        prompt_template = self._load_prompt()

        # Replace prompt placeholders.
        prompt = (
            prompt_template.replace("{characters}", character_json)
            .replace(
                "{chapter_number}",
                str(chapter_number) if chapter_number is not None else "Not provided",
            )
            .replace("{story_text}", story_text.strip())
        )

        # Request structured event information.
        result = self.llm_client.generate_structured(
            prompt=prompt,
            response_schema=EventExtractionResult,
        )

        # Resolve participants to canonical character names.
        character_lookup = {}

        for character in characters.characters:
            character_lookup[character.name.strip().casefold()] = character.name

            for alias in character.aliases:
                character_lookup[alias.strip().casefold()] = character.name

        validated_events = []

        for event in result.events:

            canonical_participants = []

            for participant in event.participants:
                key = participant.strip().casefold()

                if key not in character_lookup:
                    raise ValueError(f"Unknown event participant: {participant}")

                canonical_name = character_lookup[key]

                if canonical_name not in canonical_participants:
                    canonical_participants.append(canonical_name)

            # Preserve the supplied chapter number.
            final_chapter = (
                chapter_number if chapter_number is not None else event.chapter_number
            )

            validated_events.append(
                event.model_copy(
                    update={
                        "participants": canonical_participants,
                        "chapter_number": final_chapter,
                    }
                )
            )

        return EventExtractionResult(events=validated_events)

    def close(self):
        """Close the client only if this class owns it."""

        if self._owns_client:
            self.llm_client.close()
