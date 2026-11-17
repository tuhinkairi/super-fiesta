"""
LLM adapter for content generation.

Connects the generation layer with the provider-independent
LLM service.
"""

from __future__ import annotations

from collections.abc import Sequence
from time import perf_counter

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GeneratedContent,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
)
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.models import LLMRequest
from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.llm.service import LLMService


class LLMGenerationAdapter(BaseGenerationProvider):
    """Adapts an LLM service to the generation provider interface."""

    def __init__(self, llm_service: LLMService) -> None:
        if not isinstance(llm_service, LLMService):
            raise TypeError(
                "llm_service must be an LLMService instance."
            )

        self.llm_service = llm_service

    def connect(self) -> bool:
        """Connect through the underlying LLM service."""
        return self.llm_service.provider.connect()

    def health_check(self) -> bool:
        """Check the underlying LLM service."""
        return self.llm_service.health_check()

    def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Generate content using the underlying LLM service."""

        if not isinstance(request, GenerationRequest):
            raise TypeError(
                "request must be a GenerationRequest instance."
            )

        start_time = perf_counter()

        try:
            parameters = request.parameters

            llm_request = LLMRequest(
                prompt=request.prompt,
                system_instruction=request.instructions or None,
                temperature=parameters.temperature,
                top_p=parameters.top_p,
                top_k=parameters.top_k,
                max_output_tokens=parameters.max_output_tokens,
                stop_sequences=list(parameters.stop_sequences),
                metadata=request.metadata.copy(),
            )

            llm_response = self.llm_service.generate(llm_request)

            generated_content = GeneratedContent(
                content=llm_response.text,
                request_id=request.request_id,
                content_format=request.content_format,
                model=llm_response.model,
                recommendation_id=request.recommendation_id,
                language=request.language,
                metadata={
                    **request.metadata,
                    "provider": llm_response.provider,
                    "prompt_tokens": llm_response.usage.prompt_tokens,
                    "completion_tokens": llm_response.usage.completion_tokens,
                    "total_tokens": llm_response.usage.total_tokens,
                    "latency_ms": llm_response.latency_ms,
                },
            )

            return GenerationResult(
                request_id=request.request_id,
                status=GenerationStatus.COMPLETED,
                generated_content=generated_content,
                execution_time_ms=(perf_counter() - start_time) * 1000,
                model=llm_response.model,
                metadata={
                    "provider": llm_response.provider,
                    "finish_reason": llm_response.finish_reason,
                },
            )

        except Exception as exc:
            return GenerationResult(
                request_id=request.request_id,
                status=GenerationStatus.FAILED,
                error=str(exc),
                execution_time_ms=(perf_counter() - start_time) * 1000,
                warnings=[],
            )

    def generate_many(
        self,
        requests: Sequence[GenerationRequest],
    ) -> list[GenerationResult]:
        """Generate content for multiple requests."""

        if isinstance(requests, (str, bytes)):
            raise TypeError(
                "requests must be a sequence of GenerationRequest objects."
            )

        if not isinstance(requests, Sequence):
            raise TypeError("requests must be a sequence.")

        if not all(
            isinstance(request, GenerationRequest)
            for request in requests
        ):
            raise TypeError(
                "Every item must be a GenerationRequest instance."
            )

        return [
            self.generate(request)
            for request in requests
        ]

    def close(self) -> None:
        """Close the underlying LLM service."""
        self.llm_service.close()
