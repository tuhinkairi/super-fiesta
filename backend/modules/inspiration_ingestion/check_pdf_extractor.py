from pathlib import Path
from tempfile import TemporaryDirectory

import pymupdf

from modules.inspiration_ingestion.extractors.pdf_extractor import (
    PDFExtractor,
)


def main():
    with TemporaryDirectory() as temp_dir:
        # Create a sample PDF for testing.
        pdf_path = Path(temp_dir) / "sample.pdf"

        document = pymupdf.open()
        page1 = document.new_page()
        page1.insert_text((72, 72), "Introduction to Artificial Intelligence.")

        page2 = document.new_page()
        page2.insert_text((72, 72), "Machine learning is a subset of AI.")

        document.save(pdf_path)
        document.close()

        # Extract text.
        extractor = PDFExtractor()
        result = extractor.extract_text(pdf_path)

        print("PDF extraction successful!")
        print("\nExtracted text:")
        print(result["text"])
        print("\nPage count:", result["page_count"])
        print("Contains text:", result["has_text"])

        # Verify results.
        assert result["page_count"] == 2
        assert result["has_text"] is True
        assert "Artificial Intelligence" in result["text"]
        assert "Machine learning" in result["text"]

        # Verify invalid file type rejection.
        text_file = Path(temp_dir) / "sample.txt"
        text_file.write_text("This is not a PDF.")

        try:
            extractor.extract_text(text_file)
            raise AssertionError("Non-PDF file was accepted!")
        except ValueError as error:
            print("\nInvalid file correctly rejected:", error)

        print("\nAll PDF Extractor checks passed!")


if __name__ == "__main__":
    main()
