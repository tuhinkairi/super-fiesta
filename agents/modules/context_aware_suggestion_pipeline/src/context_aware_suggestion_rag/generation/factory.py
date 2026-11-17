"""
Factories for content generation services.

Provides reusable construction of generation services
with configurable providers and supporting components.
"""

from __future__ import annotations

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.base import (
    BaseGenerationProvider,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.formatter import (
    ContentFormatter,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.service import (
    GenerationService,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.generation.validators import (
    GeneratedContentValidator,
)


def create_generation_service(
    provider: BaseGenerationProvider,
    *,
    validator: GeneratedContentValidator | None = None,
    formatter: ContentFormatter | None = None,
) -> GenerationService:
    """
    Create a configured generation service.

    Args:
        provider: Concrete generation provider.
        validator: Optional generated-content validator.
        formatter: Optional content formatter.

    Returns:
        Configured GenerationService instance.
    """

    return GenerationService(
        provider=provider,
        validator=validator,
        formatter=formatter,
    )
