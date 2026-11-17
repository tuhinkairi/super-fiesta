from pydantic import BaseModel, ConfigDict, Field

from modules.story_intelligence.llm.llm_client import LLMClient
from modules.inspiration_ingestion.config import get_inspiration_settings

from modules.inspiration_ingestion.processing.chunker import (
    TextChunker,
)


class InspirationAnalysis(BaseModel):
    """
    Structured AI analysis of an inspiration item.
    """

    model_config = ConfigDict(extra="ignore")

    summary: str = Field(description="A short summary of the provided content.")

    description: str = Field(description="A meaningful description of the content.")

    keywords: list[str] = Field(description="Important keywords found in the content.")

    themes: list[str] = Field(description="Main themes or subjects of the content.")

    mood_tags: list[str] = Field(
        description="Emotions or moods expressed by the content."
    )


class InspirationAnalyzer:
    """
    Analyzes inspiration text using Gemini.

    Long documents are divided into chunks.
    Each chunk is analyzed separately, and the results
    are combined into one InspirationAnalysis object.
    """

    def __init__(self, llm_client=None, chunker=None):

        self._owns_client = llm_client is None
        self.llm_client = llm_client or LLMClient(
            model_name=get_inspiration_settings().model_name
        )

        self.chunker = chunker or TextChunker()

    def _analyze_single_chunk(
        self,
        text: str,
    ) -> InspirationAnalysis:

        prompt = f"""
You are an intelligent creative inspiration analyst.

Analyze the content provided below.

Your tasks:
1. Write a concise summary in 2-3 sentences.
2. Describe the content and its important ideas.
3. Extract 5-10 meaningful keywords.
4. Identify the main themes.
5. Identify the emotional mood using short descriptive tags.

Important instructions:
- Base your analysis only on the supplied content.
- Do not invent facts or events.
- Avoid generic or repetitive keywords.
- Keep the summary concise.
- Return the result in the required structured format.

CONTENT:
{text}
"""

        return self.llm_client.generate_structured(
            prompt=prompt,
            response_schema=InspirationAnalysis,
        )

    @staticmethod
    def _combine_unique_text(values: list[str]) -> str:
        """
        Combine text while removing exact duplicate entries.
        """

        unique_values = []
        seen = set()

        for value in values:
            cleaned = value.strip()

            if cleaned and cleaned.casefold() not in seen:
                seen.add(cleaned.casefold())
                unique_values.append(cleaned)

        return " ".join(unique_values)

    @staticmethod
    def _combine_unique_lists(
        values: list[list[str]],
    ) -> list[str]:
        """
        Combine lists while preserving order and removing duplicates.
        """

        combined = []
        seen = set()

        for group in values:
            for item in group:
                cleaned = item.strip()
                normalized = cleaned.casefold()

                if cleaned and normalized not in seen:
                    seen.add(normalized)
                    combined.append(cleaned)

        return combined

    def analyze_text(self, text: str) -> InspirationAnalysis:
        """
        Analyze short or long text.

        Short text uses one AI request.
        Long text uses one request per chunk.
        """

        if not text or not text.strip():
            raise ValueError("Text to analyze cannot be empty.")

        chunks = self.chunker.chunk_text(text)

        if not chunks:
            raise ValueError("No readable text chunks were produced.")

        analyses = []

        for index, chunk in enumerate(chunks, start=1):

            print(
                f"Analyzing text chunk {index}/{len(chunks)}...",
                flush=True,
            )

            analysis = self._analyze_single_chunk(chunk)
            analyses.append(analysis)

        return InspirationAnalysis(
            summary=self._combine_unique_text([item.summary for item in analyses]),
            description=self._combine_unique_text(
                [item.description for item in analyses]
            ),
            keywords=self._combine_unique_lists([item.keywords for item in analyses]),
            themes=self._combine_unique_lists([item.themes for item in analyses]),
            mood_tags=self._combine_unique_lists([item.mood_tags for item in analyses]),
        )

    def close(self):

        if self._owns_client:
            self.llm_client.close()
