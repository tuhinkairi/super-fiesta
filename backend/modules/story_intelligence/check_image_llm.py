from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from modules.story_intelligence.llm.llm_client import LLMClient


class SampleResponse(BaseModel):
    description: str


def main():

    with TemporaryDirectory() as temp_dir:

        # Create a small valid PNG image.
        from PIL import Image

        image_path = Path(temp_dir) / "sample.png"

        image = Image.new("RGB", (100, 100), color="blue")
        image.save(image_path)

        # Create an LLMClient without initializing Gemini.
        llm = LLMClient.__new__(LLMClient)

        mock_response = MagicMock()
        mock_response.text = '{"description": "A blue square."}'

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        llm.client = mock_client
        llm.model = "test-model"

        # Test the image method.
        with patch(
            "modules.story_intelligence.llm.llm_client.genai_types.Part.from_text",
            return_value="mock text part",
        ), patch(
            "modules.story_intelligence.llm.llm_client.genai_types.Part.from_bytes",
            return_value="mock image part",
        ), patch(
            "modules.story_intelligence.llm.llm_client.genai_types.GenerateContentConfig",
            return_value="mock config",
        ):

            result = llm.generate_image_structured(
                prompt="Describe this image.",
                image_path=image_path,
                response_schema=SampleResponse,
            )

        print("Image LLM method executed successfully!")
        print("Description:", result.description)

        assert result.description == "A blue square."

        # Verify Gemini received an image request.
        mock_client.models.generate_content.assert_called_once()

        # Verify missing image is rejected.
        try:
            llm.generate_image_structured(
                prompt="Describe this image.",
                image_path=Path(temp_dir) / "missing.png",
                response_schema=SampleResponse,
            )

            raise AssertionError("Missing image should have been rejected.")

        except FileNotFoundError:
            print("Missing image correctly rejected.")

        # Verify empty prompt is rejected.
        try:
            llm.generate_image_structured(
                prompt="",
                image_path=image_path,
                response_schema=SampleResponse,
            )

            raise AssertionError("Empty prompt should have been rejected.")

        except ValueError:
            print("Empty prompt correctly rejected.")

    print("\nAll Image LLM checks passed!")


if __name__ == "__main__":
    main()
