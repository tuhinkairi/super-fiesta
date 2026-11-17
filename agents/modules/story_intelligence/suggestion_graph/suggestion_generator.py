
from pathlib import Path
from typing import Any

from modules.story_intelligence.llm.llm_client import LLMClient
from modules.story_intelligence.models.graph import StoryKnowledgeGraph
from modules.story_intelligence.models.suggestion import SuggestionGraph


class SuggestionGenerator:
    """
    Generates hypothetical story suggestions using:
    1. An approved canonical knowledge graph.
    2. Additional story context.
    3. Optional inspiration retrieved from Inspiration Ingestion.

    Inspiration is reference material only. It never becomes
    an established canonical story fact automatically.
    """

    def __init__(self, llm_client: LLMClient | None = None):
        self._owns_client = llm_client is None

        self.llm_client = (
            llm_client if llm_client is not None else LLMClient()
        )

        self.prompt_path = (
            Path(__file__).resolve().parent.parent
            / "llm"
            / "prompts"
            / "suggestion_generation.txt"
        )

    def _load_prompt(self) -> str:
        """Load the suggestion-generation instructions."""

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Suggestion prompt not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8")

    @staticmethod
    def _get_value(record: Any, field: str, default: Any = "") -> Any:
        """Read a field from either a Pydantic object or a dictionary."""

        if isinstance(record, dict):
            return record.get(field, default)

        return getattr(record, field, default)

    def _format_inspiration_context(
        self,
        inspiration_results: list[dict] | None,
    ) -> str:
        """
        Convert semantic-search results into readable prompt context.

        Only selected descriptive fields are included.
        Embeddings and internal storage information are excluded.
        """

        if not inspiration_results:
            return "No external inspiration references were provided."

        formatted_references = []

        for index, result in enumerate(inspiration_results, start=1):
            if not isinstance(result, dict):
                continue

            record = result.get("record")

            if record is None:
                continue

            record_id = self._get_value(record, "id", "unknown")
            file_name = self._get_value(record, "file_name", "Untitled")
            content_type = self._get_value(
                record, "content_type", "unknown"
            )
            source = self._get_value(record, "source", "")
            summary = self._get_value(record, "summary", "")
            description = self._get_value(record, "description", "")
            extracted_text = self._get_value(
                record, "extracted_text", ""
            )
            keywords = self._get_value(record, "keywords", [])
            themes = self._get_value(record, "themes", [])
            mood_tags = self._get_value(record, "mood_tags", [])

            similarity = result.get("similarity")

            reference = [
                f"INSPIRATION REFERENCE {index}",
                f"Reference ID: {record_id}",
                f"Title / File name: {file_name}",
                f"Content type: {content_type}",
            ]

            if similarity is not None:
                reference.append(
                    f"Semantic similarity: {similarity}"
                )

            if source:
                reference.append(f"Original source: {source}")

            if summary:
                reference.append(f"Summary: {summary}")

            if description:
                reference.append(f"Description: {description}")

            if keywords:
                reference.append(f"Keywords: {', '.join(keywords)}")

            if themes:
                reference.append(f"Themes: {', '.join(themes)}")

            if mood_tags:
                reference.append(
                    f"Mood tags: {', '.join(mood_tags)}"
                )

            if extracted_text:
                # Limit prompt size while retaining useful context.
                reference.append(
                    "Extracted content: "
                    + str(extracted_text)[:1200]
                )

            formatted_references.append("\n".join(reference))

        if not formatted_references:
            return "No usable inspiration references were found."

        return "\n\n".join(formatted_references)

    def generate_suggestions(
        self,
        canonical_graph: StoryKnowledgeGraph,
        story_context: str,
        max_suggestions: int = 3,
        inspiration_results: list[dict] | None = None,
    ) -> SuggestionGraph:
        """
        Generate suggestions without changing the canonical graph.

        Inspiration results are optional and are used only as
        creative reference material.
        """

        if canonical_graph.approval_status != "approved":
            raise ValueError(
                "Suggestion generation requires an approved canonical graph."
            )

        if not story_context or not story_context.strip():
            raise ValueError("Story context cannot be empty.")

        if max_suggestions < 1:
            raise ValueError("max_suggestions must be at least 1.")

        prompt = self._load_prompt()

        formatted_inspiration = self._format_inspiration_context(
            inspiration_results
        )

        full_prompt = f"""
{prompt}

MAXIMUM NUMBER OF SUGGESTIONS:
{max_suggestions}

CANONICAL STORY KNOWLEDGE GRAPH:
{canonical_graph.model_dump_json(indent=2)}

ADDITIONAL STORY CONTEXT:
{story_context}

RETRIEVED INSPIRATION REFERENCES:
{formatted_inspiration}

IMPORTANT INTEGRATION RULES:

1. Inspiration references are creative material, not canonical story facts.
2. Never treat an inspiration reference as an existing story event,
   character, relationship, or established fact.
3. Do not use inspiration reference IDs in based_on_node_ids.
4. Use only canonical graph node IDs in based_on_node_ids.
5. When an inspiration reference genuinely informs a suggestion,
   identify it in source_evidence using its exact Reference ID.
6. Do not claim that an inspiration reference contains information
   that was not supplied above.
7. Inspiration is optional. Do not force it into every suggestion.
8. Do not copy external material as if it were original story content.

Generate no more than {max_suggestions} suggestions.
Return only data matching the requested structured output schema.
"""

        result = self.llm_client.generate_structured(
            prompt=full_prompt,
            response_schema=SuggestionGraph,
        )

        if result.project_id != canonical_graph.project_id:
            raise ValueError(
                "Generated suggestion project_id does not match "
                "the canonical graph project_id."
            )

        canonical_node_ids = {
            node.id for node in canonical_graph.nodes
        }

        for suggestion in result.suggestions:
            if suggestion.status != "proposed":
                raise ValueError(
                    "Generated suggestions must have status='proposed'."
                )

            unknown_ids = (
                set(suggestion.based_on_node_ids) - canonical_node_ids
            )

            if unknown_ids:
                raise ValueError(
                    f"Suggestion references unknown canonical nodes: "
                    f"{sorted(unknown_ids)}"
                )

        return result

    def close(self):
        """Close the LLM client only when this class owns it."""

        if self._owns_client:
            self.llm_client.close()
