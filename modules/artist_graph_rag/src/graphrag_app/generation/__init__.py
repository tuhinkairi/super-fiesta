"""
Answer generation package.

Provides components for generating grounded answers
using Gemini and retrieved knowledge graph context.
"""

from .models import (
    GenerationRequest,
    GenerationResult,
)

from .answer_generator import AnswerGenerator


__all__ = [
    "GenerationRequest",
    "GenerationResult",
    "AnswerGenerator",
]
