"""Context-Aware Suggestion RAG package."""

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.facade import (
    ContextAwareSuggestionFacade,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.pipeline import (
    ContextAwareSuggestionPipeline,
    PipelineResult,
    PipelineStage,
    PipelineStageResult,
    PipelineStatus,
)

__version__ = "0.1.0"
__author__ = "Project Author"

__all__ = [
    "__version__",
    "__author__",
    "ContextAwareSuggestionFacade",
    "ContextAwareSuggestionPipeline",
    "PipelineResult",
    "PipelineStage",
    "PipelineStageResult",
    "PipelineStatus",
]
