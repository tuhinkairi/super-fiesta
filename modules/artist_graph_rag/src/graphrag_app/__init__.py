"""
GraphRAG Application Package.

Provides a modular document-based GraphRAG system
using Gemini and Neo4j.
"""

from .application import GraphRAGApplication
from .factory import create_application

__version__ = "0.1.0"

__all__ = [
    "GraphRAGApplication",
    "create_application",
]
