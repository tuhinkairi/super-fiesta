"""
Content generation package.

Provides generation models, prompt construction, validation,
formatting, provider abstractions, and LLM integration.
"""

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.models import (
    GenerationBatchResult,
    GeneratedContent,
    GenerationMode,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.prompts import (
    DEFAULT_SYSTEM_INSTRUCTION,
    DEFAULT_USER_TEMPLATE,
    PromptBuilder,
    PromptTemplate,
    build_generation_prompt,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.validators import (
    ContentValidationConfig,
    ContentValidationResult,
    GeneratedContentValidator,
    validate_generated_content,
    validate_generation_result,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.formatter import (
    SUPPORTED_FORMATS,
    ContentFormatter,
    FormattingOptions,
    format_generated_content,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.service import (
    GenerationService,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.factory import (
    create_generation_service,
)

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.llm_adapter import (
    LLMGenerationAdapter,
)

__all__ = [
    "GenerationBatchResult",
    "GeneratedContent",
    "GenerationMode",
    "GenerationParameters",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStatus",
    "DEFAULT_SYSTEM_INSTRUCTION",
    "DEFAULT_USER_TEMPLATE",
    "PromptBuilder",
    "PromptTemplate",
    "build_generation_prompt",
    "ContentValidationConfig",
    "ContentValidationResult",
    "GeneratedContentValidator",
    "validate_generated_content",
    "validate_generation_result",
    "SUPPORTED_FORMATS",
    "ContentFormatter",
    "FormattingOptions",
    "format_generated_content",
    "BaseGenerationProvider",
    "GenerationService",
    "create_generation_service",
    "LLMGenerationAdapter",
]