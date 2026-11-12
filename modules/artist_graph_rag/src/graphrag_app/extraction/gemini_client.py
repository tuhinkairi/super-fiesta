
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from graphrag_app.config import settings


class GeminiClient:
    """Provides a centralized LangChain interface to Google Gemini."""

    def __init__(self):
        self.model_name = settings.llm_model

        self._model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=settings.llm_api_key,
            temperature=0.2,
        )

    @staticmethod
    def _extract_text(content: Any) -> str:
        """Converts LangChain response content into plain text."""

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            text_parts = []

            for item in content:
                if isinstance(item, str):
                    text_parts.append(item)
                elif isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

            return "\n".join(text_parts).strip()

        raise TypeError(
            f"Unsupported Gemini response content type: {type(content).__name__}"
        )

    def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int | None = None,
    ) -> str:
        """Generates text using Gemini through LangChain."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if not 0.0 <= temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0.")

        messages = []

        if system_instruction:
            messages.append(
                SystemMessage(content=system_instruction)
            )

        messages.append(HumanMessage(content=prompt))

        model = self._model.bind(temperature=temperature)

        if max_output_tokens is not None:
            if max_output_tokens < 1:
                raise ValueError("max_output_tokens must be positive.")

            model = model.bind(
                max_output_tokens=max_output_tokens
            )

        response = model.invoke(messages)

        return self._extract_text(response.content)
