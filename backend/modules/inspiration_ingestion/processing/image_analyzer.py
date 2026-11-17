from pathlib import Path

from modules.story_intelligence.llm.llm_client import LLMClient

from modules.inspiration_ingestion.extractors.image_extractor import (
    ImageExtractor,
)

from modules.inspiration_ingestion.processing.analyzer import (
    InspirationAnalysis,
)


class ImageAnalyzer:
    """
    Uses Gemini's multimodal capabilities to understand
    and describe inspiration images.
    """

    def __init__(self, llm_client=None):
        self._owns_client = llm_client is None
        self.llm_client = llm_client or LLMClient()

        self.image_extractor = ImageExtractor()

    def analyze_image(
        self,
        image_path: str | Path,
    ) -> InspirationAnalysis:
        """
        Analyze an image and return structured metadata.
        """

        path = Path(image_path)

        # Validate the image and retrieve its metadata.
        metadata = self.image_extractor.extract_metadata(path)

        prompt = f"""
You are an intelligent visual inspiration analyst.

Analyze the supplied image.

Your tasks:
1. Write a concise summary of the image.
2. Describe its visible content, objects, setting,
   composition, and visual characteristics.
3. Extract 5-10 meaningful keywords.
4. Identify its main themes.
5. Identify its emotional mood using short descriptive tags.

Important instructions:
- Describe only what is visibly supported by the image.
- Do not invent objects, people, events, or context.
- Do not identify real people.
- Avoid generic or repetitive keywords.
- Keep the summary concise.
- Return the result in the required structured format.

Image information:
- File name: {metadata["file_name"]}
- Format: {metadata["format"]}
- Dimensions: {metadata["width"]} x {metadata["height"]}
"""

        return self.llm_client.generate_image_structured(
            prompt=prompt,
            image_path=path,
            response_schema=InspirationAnalysis,
        )

    def close(self):
        """
        Close the LLM client only if this analyzer created it.
        """

        if self._owns_client:
            self.llm_client.close()
