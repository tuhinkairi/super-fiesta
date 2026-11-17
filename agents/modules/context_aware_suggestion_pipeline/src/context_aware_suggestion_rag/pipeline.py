"""Main orchestration pipeline for Context-Aware Suggestion RAG."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import WorkflowError


logger = logging.getLogger(__name__)


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class PipelineStatus(str, Enum):
    """Possible pipeline execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class PipelineStage:
    """A named pipeline stage."""

    name: str
    handler: Callable[[dict[str, Any]], Any]
    required: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Stage name must be a non-empty string.")

        if not callable(self.handler):
            raise TypeError("Stage handler must be callable.")

        if not isinstance(self.required, bool):
            raise TypeError("Stage required must be a boolean.")


@dataclass(slots=True)
class PipelineStageResult:
    """Execution details for an individual pipeline stage."""

    name: str
    success: bool
    output: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(slots=True)
class PipelineResult:
    """Complete result of a pipeline execution."""

    execution_id: str
    status: PipelineStatus
    input_data: dict[str, Any]
    output_data: dict[str, Any] = field(default_factory=dict)
    stage_results: list[PipelineStageResult] = field(
        default_factory=list
    )
    error: str | None = None
    started_at: datetime = field(default_factory=current_utc_time)
    completed_at: datetime | None = None
    execution_time_ms: float = 0.0

    @property
    def successful_stages(self) -> int:
        return sum(stage.success for stage in self.stage_results)

    @property
    def failed_stages(self) -> int:
        return sum(not stage.success for stage in self.stage_results)

    @property
    def is_successful(self) -> bool:
        return self.status == PipelineStatus.COMPLETED


class ContextAwareSuggestionPipeline:
    """Execute configured stages in a controlled sequence."""

    def __init__(
        self,
        stages: Sequence[PipelineStage],
        *,
        stop_on_error: bool = False,
    ) -> None:
        if not isinstance(stages, Sequence) or isinstance(
            stages, (str, bytes)
        ):
            raise TypeError("stages must be a sequence.")

        if not stages:
            raise ValueError("At least one pipeline stage is required.")

        if any(not isinstance(stage, PipelineStage) for stage in stages):
            raise TypeError(
                "Every pipeline stage must be a PipelineStage instance."
            )

        names = [stage.name for stage in stages]

        if len(names) != len(set(names)):
            raise ValueError("Pipeline stage names must be unique.")

        if not isinstance(stop_on_error, bool):
            raise TypeError("stop_on_error must be a boolean.")

        self.stages = tuple(stages)
        self.stop_on_error = stop_on_error

    def run(
        self,
        input_data: Mapping[str, Any],
    ) -> PipelineResult:
        """Execute the pipeline using the supplied input mapping."""

        if not isinstance(input_data, Mapping):
            raise TypeError("input_data must be a mapping.")

        state = dict(input_data)
        execution_id = f"pipeline_{uuid4().hex}"

        result = PipelineResult(
            execution_id=execution_id,
            status=PipelineStatus.RUNNING,
            input_data=dict(state),
        )

        pipeline_start = time.perf_counter()

        logger.info(
            "Pipeline execution started: %s",
            execution_id,
        )

        for stage in self.stages:
            stage_start = time.perf_counter()
            started_at = current_utc_time()

            logger.info(
                "Executing pipeline stage '%s'.",
                stage.name,
            )

            try:
                stage_output = stage.handler(dict(state))

                if isinstance(stage_output, Mapping):
                    state.update(stage_output)
                elif stage_output is not None:
                    state[stage.name] = stage_output

                result.stage_results.append(
                    PipelineStageResult(
                        name=stage.name,
                        success=True,
                        output=stage_output,
                        execution_time_ms=(
                            time.perf_counter() - stage_start
                        ) * 1000,
                        started_at=started_at,
                        completed_at=current_utc_time(),
                    )
                )

            except Exception as exc:
                logger.exception(
                    "Pipeline stage '%s' failed.",
                    stage.name,
                )

                result.stage_results.append(
                    PipelineStageResult(
                        name=stage.name,
                        success=False,
                        error=str(exc),
                        execution_time_ms=(
                            time.perf_counter() - stage_start
                        ) * 1000,
                        started_at=started_at,
                        completed_at=current_utc_time(),
                    )
                )

                if stage.required or self.stop_on_error:
                    result.status = PipelineStatus.FAILED
                    result.error = (
                        f"Pipeline stage '{stage.name}' failed: {exc}"
                    )
                    break

            result.output_data = dict(state)

        else:
            result.status = PipelineStatus.COMPLETED

        result.output_data = dict(state)
        result.completed_at = current_utc_time()
        result.execution_time_ms = (
            time.perf_counter() - pipeline_start
        ) * 1000

        logger.info(
            "Pipeline execution finished: %s (%s)",
            execution_id,
            result.status.value,
        )

        return result

    def get_stage_names(self) -> tuple[str, ...]:
        """Return the configured stage names in execution order."""
        return tuple(stage.name for stage in self.stages)


__all__ = [
    "PipelineStatus",
    "PipelineStage",
    "PipelineStageResult",
    "PipelineResult",
    "ContextAwareSuggestionPipeline",
    "current_utc_time",
]
