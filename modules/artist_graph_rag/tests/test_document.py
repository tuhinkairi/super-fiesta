from pathlib import Path

from docx import Document
from pypdf import PdfWriter

from graphrag_app.document import (
    DocumentExtractor,
    DocumentService,
    TextCleaner,
)


def test_txt_extraction(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text(
        "Machine Learning is a branch of AI.",
        encoding="utf-8",
    )

    extractor = DocumentExtractor()
    text = extractor.extract(file_path)

    assert "Machine Learning" in text


def test_pdf_extraction(tmp_path: Path):
    file_path = tmp_path / "sample.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    with file_path.open("wb") as file:
        writer.write(file)

    extractor = DocumentExtractor()

    try:
        extractor.extract(file_path)
        assert False, "Expected empty PDF to raise ValueError"
    except ValueError as error:
        assert "No readable text" in str(error)


def test_docx_extraction(tmp_path: Path):
    file_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph(
        "Artificial Intelligence is transforming technology."
    )
    document.save(file_path)

    extractor = DocumentExtractor()
    text = extractor.extract(file_path)

    assert "Artificial Intelligence" in text


def test_text_cleaning():
    cleaner = TextCleaner()

    raw_text = "Machine   Learning\n\n\nis a branch of AI."

    cleaned_text = cleaner.clean(raw_text)

    assert cleaned_text == (
        "Machine Learning\n\nis a branch of AI."
    )


def test_document_service(tmp_path: Path):
    file_path = tmp_path / "research.txt"

    file_path.write_text(
        "GraphRAG combines knowledge graphs and retrieval.",
        encoding="utf-8",
    )

    service = DocumentService()

    result = service.process(
        file_path=file_path,
        document_id="test-document-001",
    )

    assert result.document_id == "test-document-001"
    assert result.filename == "research.txt"
    assert result.character_count == len(result.text)
    assert "GraphRAG" in result.text


def test_missing_document(tmp_path: Path):
    service = DocumentService()

    try:
        service.process(
            file_path=tmp_path / "missing.txt",
            document_id="missing-document",
        )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_unsupported_file(tmp_path: Path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("name,subject", encoding="utf-8")

    extractor = DocumentExtractor()

    try:
        extractor.extract(file_path)
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "Unsupported document extension" in str(error)
