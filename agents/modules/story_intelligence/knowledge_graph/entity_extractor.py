
from pathlib import Path

from modules.story_intelligence.llm.llm_client import LLMClient

from modules.story_intelligence.models.character import (
    CharacterExtractionResult,
)


class EntityExtractor:
    """
    Extracts characters from story text using Gemini.

    Supports an externally injected LLM client so the
    orchestrator can share one client across extractors.
    """

    def __init__(self, llm_client: LLMClient | None = None):

        # Track whether this extractor owns the client.
        self._owns_client = llm_client is None

        # Use an injected client or create a new one.
        self.llm_client = (
            llm_client
            if llm_client is not None
            else LLMClient()
        )

        # Locate the character extraction prompt.
        self.prompt_path = (
            Path(__file__).resolve().parent.parent
            / "llm"
            / "prompts"
            / "entity_extraction.txt"
        )

    def _load_prompt(self) -> str:
        """
        Load character extraction instructions.
        """

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Character extraction prompt not found: "
                f"{self.prompt_path}"
            )

        return self.prompt_path.read_text(
            encoding="utf-8"
        )

    def extract_characters(
        self,
        story_text: str,
    ) -> CharacterExtractionResult:
        """
        Extract characters from the supplied story passage.
        """

        if not story_text or not story_text.strip():
            raise ValueError(
                "Story text cannot be empty."
            )

        # Load extraction instructions.
        prompt_template = self._load_prompt()

        # Make sure the prompt contains the expected placeholder.
        if "{story_text}" not in prompt_template:
            raise ValueError(
                "The character extraction prompt must contain "
                "the {story_text} placeholder."
            )

        # Insert the actual story into the prompt.
        prompt = prompt_template.replace(
            "{story_text}",
            story_text.strip(),
        )

        # Request structured character information.
        result = self.llm_client.generate_structured(
            prompt=prompt,
            response_schema=CharacterExtractionResult,
        )

        return result

    def close(self) -> None:
        """
        Close the client only if this extractor created it.
        """

        if self._owns_client:
            self.llm_client.close()
