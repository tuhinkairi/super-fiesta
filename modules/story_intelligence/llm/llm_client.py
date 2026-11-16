
import mimetypes
from pathlib import Path
from typing import TypeVar

from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel

from modules.story_intelligence.config import get_settings


T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """
    Handles communication between Story Intelligence
    and Gemini for text and multimodal requests.
    """

    SUPPORTED_IMAGE_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    }

    def __init__(self):
        settings = get_settings()

        api_key = settings.gemini_api_key.get_secret_value()

        if not api_key.strip():
            raise ValueError("Gemini API key is missing.")

        self.model = settings.gemini_model
        self.client = genai.Client(api_key=api_key)

    def _create_interaction(
        self,
        prompt: str,
        response_schema: type[BaseModel] | None = None,
    ):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        print("Sending request to Gemini...", flush=True)

        try:
            if response_schema is None:
                interaction = self.client.interactions.create(
                    model=self.model,
                    input=prompt,
                )
            else:
                interaction = self.client.interactions.create(
                    model=self.model,
                    input=prompt,
                    response_format={
                        "type": "text",
                        "mime_type": "application/json",
                        "schema": response_schema.model_json_schema(),
                    },
                )

            return interaction

        except Exception as error:
            raise RuntimeError(
                f"Gemini API request failed: {error}"
            ) from error

    def generate_text(self, prompt: str) -> str:
        interaction = self._create_interaction(prompt)

        if not interaction.output_text:
            raise RuntimeError("Gemini returned an empty response.")

        return interaction.output_text.strip()

    def generate_structured(
        self,
        prompt: str,
        response_schema: type[T],
    ) -> T:

        interaction = self._create_interaction(
            prompt=prompt,
            response_schema=response_schema,
        )

        if not interaction.output_text:
            raise RuntimeError(
                "Gemini returned an empty structured response."
            )

        try:
            return response_schema.model_validate_json(
                interaction.output_text
            )

        except Exception as error:
            raise RuntimeError(
                f"Gemini returned invalid structured data: {error}"
            ) from error

    def generate_image_structured(
        self,
        prompt: str,
        image_path: str | Path,
        response_schema: type[T],
    ) -> T:
        """
        Send a local image and prompt to Gemini.
        Return the response in a Pydantic structured format.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Image not found: {path}"
            )

        if not path.is_file():
            raise ValueError(
                "The provided image path is not a file."
            )

        mime_type, _ = mimetypes.guess_type(str(path))

        if mime_type not in self.SUPPORTED_IMAGE_TYPES:
            raise ValueError(
                f"Unsupported image MIME type: {mime_type}"
            )

        try:
            image_bytes = path.read_bytes()

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    genai_types.Part.from_text(
                        text=prompt
                    ),
                    genai_types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                ],
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema,
                ),
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty image analysis."
                )

            return response_schema.model_validate_json(
                response.text
            )

        except Exception as error:
            raise RuntimeError(
                f"Gemini image analysis failed: {error}"
            ) from error

    def generate_embedding(self, text: str) -> list[float]:
        """
        Convert text into a numerical embedding vector.
        """

        if not text or not text.strip():
            raise ValueError("Text for embedding cannot be empty.")

        try:
            response = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text.strip(),
                config=genai_types.EmbedContentConfig(
                    output_dimensionality=768,
                ),
            )

            if (
                not response.embeddings
                or not response.embeddings[0].values
            ):
                raise RuntimeError(
                    "Gemini returned an empty embedding."
                )

            return [
                float(value)
                for value in response.embeddings[0].values
            ]

        except Exception as error:
            raise RuntimeError(
                f"Gemini embedding generation failed: {error}"
            ) from error

    def close(self) -> None:
        self.client.close()
