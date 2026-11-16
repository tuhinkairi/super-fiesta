"""
Document processing package.

Provides functionality for extracting, cleaning,
and preparing text from PDF, DOCX, and TXT documents.
"""

from .models import ExtractedDocument

from .txt_extractor import TXTExtractor
from .pdf_extractor import PDFExtractor
from .docx_extractor import DOCXExtractor

from .extractor import DocumentExtractor
from .cleaner import TextCleaner
from .service import DocumentService


__all__ = [
    "ExtractedDocument",
    "TXTExtractor",
    "PDFExtractor",
    "DOCXExtractor",
    "DocumentExtractor",
    "TextCleaner",
    "DocumentService",
]
