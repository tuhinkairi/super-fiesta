"""Public facade for the Context-Aware Suggestion RAG package."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import WorkflowError
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.pipeline import (
    ContextAwareSuggestionPipeline,
    PipelineResult,
    PipelineStatus,
)


class ContextAwareSuggestionFacade:
    """Provide a simplified public interface to the RAG pipeline."""

    def __init__(
        self,
        pipeline: ContextAwareSuggestionPipeline,
    ) -> None:
        if not isinstance(
            pipeline,
            ContextAwareSuggestionPipeline,
        ):
            raise TypeError(
                "pipeline must be a ContextAwareSuggestionPipeline."
            )

        self._pipeline = pipeline
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise WorkflowError("The pipeline facade is closed.")

    def execute(
        self,
        input_data: Mapping[str, Any],
    ) -> PipelineResult:
        """Execute the pipeline and return its result."""

        self._ensure_open()

        return self._pipeline.run(input_data)

    def execute_or_raise(
        self,
        input_data: Mapping[str, Any],
    ) -> PipelineResult:
        """Execute the pipeline and raise if execution fails."""

        result = self.execute(input_data)

        if result.status == PipelineStatus.FAILED:
            raise WorkflowError(
                result.error or "Pipeline execution failed."
            )

        return result

    def get_stage_names(self) -> tuple[str, ...]:
        """Return the configured pipeline stages."""

        self._ensure_open()

        return self._pipeline.get_stage_names()

    def health_check(self) -> bool:
        """Check whether the facade and pipeline are available."""

        if self._closed:
            return False

        try:
            stages = self._pipeline.get_stage_names()

            return bool(stages) and all(
                callable(stage.handler)
                for stage in self._pipeline.stages
            )
        except Exception:
            return False

    def close(self) -> None:
        """Close the facade."""

        self._closed = True

    def __enter__(self) -> ContextAwareSuggestionFacade:
        self._ensure_open()
        return self

    def __exit__(
        self,
        exc_type: Any,
        exc_value: Any,
        traceback: Any,
    ) -> None:
        self.close()


__all__ = [
    "ContextAwareSuggestionFacade",
]
