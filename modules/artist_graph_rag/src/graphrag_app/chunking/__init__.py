"""
Document chunking package.

Provides components for configuring chunking strategies
and converting extracted documents into structured chunks.
"""

from .models import DocumentChunk
from .strategy import ChunkingConfig, CharacterChunkingStrategy
from .service import ChunkingService

__all__ = [
    "DocumentChunk",
    "ChunkingConfig",
    "CharacterChunkingStrategy",
    "ChunkingService",
]
