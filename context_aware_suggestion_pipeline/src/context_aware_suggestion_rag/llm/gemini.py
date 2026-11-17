"""
Google Gemini LLM provider.

Implements the common LLM provider interface using
the official Google Gen AI SDK.
"""

from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter
from typing import Any

from google import genai
from google.genai import types

from context_aware_suggestion_rag.config.llm_config import (
    get_llm_config,
)
from context_aware_suggestion_rag.core.logging import get_logger
from context_aware_suggestion_rag.exceptions import LLMError
from context_aware_suggestion_rag.llm.base import BaseLLMProvider
from context_aware_suggestion_rag.llm.models import (
    LLMRequest,
    LLMResponse,
    LLMUsage,
)


class GeminiProvider(BaseLLMProvider):
    """LLM provider implementation for Google Gemini."""

    PROVIDER_NAME = "google_gemini"

    def __init__(self) -> None:
        self.config = get_llm_config()
        self.logger = get_logger(__name__)
        self._client: genai.Client | None = None

    def connect(self) -> bool:
        """Initialize the Gemini client."""

        try:
            if self._client is not None:
                return True

            api_key = self.config.api_key.get_secret_value()

            if not api_key:
                raise LLMError(
                    "Gemini API key is not configured."
                )

            self._client = genai.Client(api_key=api_key)

            return True

        except LLMError:
            raise

        except Exception as exc:
            raise LLMError(
                f"Failed to initialize Gemini client: {exc}"
            ) from exc

    def health_check(self) -> bool:
        """Check whether the Gemini client is initialized."""

        try:
            self.connect()
            return self._client is not None

        except Exception as exc:
            self.logger.warning(
                "Gemini health check failed: %s",
                exc,
            )
            return False

    def _build_config(
        self,
        request: LLMRequest,
    ) -> types.GenerateContentConfig:
        """Build Gemini generation configuration."""

        return types.GenerateContentConfig(
            system_instruction=request.system_instruction,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            max_output_tokens=request.max_output_tokens,
            stop_sequences=request.stop_sequences or None,
        )

    @staticmethod
    def _extract_usage(
        response: Any,
    ) -> LLMUsage:
        """Extract token usage from Gemini response metadata."""

        usage_metadata = getattr(
            response,
            "usage_metadata",
            None,
        )

        if usage_metadata is None:
            return LLMUsage()

        prompt_tokens = getattr(
            usage_metadata,
            "prompt_token_count",
            0,
        ) or 0

        completion_tokens = getattr(
            usage_metadata,
            "candidates_token_count",
            0,
        ) or 0

        total_tokens = getattr(
            usage_metadata,
            "total_token_count",
            0,
        ) or 0

        return LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

    def generate(
        self,
        request: LLMRequest,
    ) -> LLMResponse:
        """Generate content using Gemini."""

        if not isinstance(request, LLMRequest):
            raise TypeError(
                "request must be an LLMRequest instance."
            )

        self.connect()

        if self._client is None:
            raise LLMError(
                "Gemini client is not initialized."
            )

        model = request.model or self.config.model

        if not model:
            raise LLMError(
                "No Gemini model has been configured."
            )

        start_time = perf_counter()

        try:
            response = self._client.models.generate_content(
                model=model,
                contents=request.prompt,
                config=self._build_config(request),
            )

            latency_ms = (
                perf_counter() - start_time
            ) * 1000

            generated_text = getattr(
                response,
                "text",
                None,
            )

            if generated_text is None:
                raise LLMError(
                    "Gemini returned an empty response."
                )

            candidates = getattr(
                response,
                "candidates",
                None,
            ) or []

            finish_reason = None

            if candidates:
                reason = getattr(
                    candidates[0],
                    "finish_reason",
                    None,
                )

                finish_reason = (
                    str(reason) if reason is not None else None
                )

            return LLMResponse(
                text=generated_text,
                model=model,
                provider=self.PROVIDER_NAME,
                usage=self._extract_usage(response),
                finish_reason=finish_reason,
                latency_ms=latency_ms,
                metadata={
                    "request_metadata": request.metadata,
                },
            )

        except LLMError:
            raise

        except Exception as exc:
            self.logger.exception(
                "Gemini generation failed."
            )

            raise LLMError(
                f"Gemini generation failed: {exc}"
            ) from exc

    def generate_many(
        self,
        requests: Sequence[LLMRequest],
    ) -> list[LLMResponse]:
        """Generate responses sequentially for multiple requests."""

        if isinstance(requests, (str, bytes)):
            raise TypeError(
                "requests must be a sequence of LLMRequest objects."
            )

        if not isinstance(requests, Sequence):
            raise TypeError(
                "requests must be a sequence."
            )

        if not all(
            isinstance(request, LLMRequest)
            for request in requests
        ):
            raise TypeError(
                "Every item must be an LLMRequest instance."
            )

        results: list[LLMResponse] = []

        for request in requests:
            results.append(self.generate(request))

        return results

    def close(self) -> None:
        """Close the Gemini client."""

        if self._client is None:
            return

        try:
            self._client.close()
        except Exception as exc:
            self.logger.warning(
                "Error while closing Gemini client: %s",
                exc,
            )
        finally:
            self._client = None
