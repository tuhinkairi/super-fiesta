"""
Knowledge extraction package.

Provides Gemini-powered entity and relationship
extraction from document chunks.
"""

from .gemini_client import GeminiClient

from .models import (
    ExtractedEntity,
    ExtractedRelationship,
    ChunkExtractionResult,
)

from .entity_extractor import EntityExtractor
from .relationship_extractor import RelationshipExtractor
from .service import ExtractionService


__all__ = [
    "GeminiClient",
    "ExtractedEntity",
    "ExtractedRelationship",
    "ChunkExtractionResult",
    "EntityExtractor",
    "RelationshipExtractor",
    "ExtractionService",
]
