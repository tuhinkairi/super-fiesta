
from pathlib import Path
from tempfile import TemporaryDirectory

from context_aware_suggestion_rag.interfaces.document_parser import (
    DocumentParser,
)


class FakeTextParser(DocumentParser):

    def parse(self, file_path: str | Path) -> str:
        return Path(file_path).read_text(encoding="utf-8")

    def supports(self, file_path: str | Path) -> bool:
        return Path(file_path).suffix.lower() == ".txt"


def main():
    parser = FakeTextParser()

    with TemporaryDirectory() as directory:
        file_path = Path(directory) / "sample.txt"
        file_path.write_text("Document parser test.", encoding="utf-8")

        assert parser.supports(file_path)
        print("Parser format detection: PASS")

        assert parser.validate(file_path)
        print("Parser file validation: PASS")

        assert parser.parse(file_path) == "Document parser test."
        print("Parser text extraction: PASS")

        assert parser.extract_metadata(file_path) == {}
        print("Default metadata extraction: PASS")

        missing_file = Path(directory) / "missing.txt"
        assert not parser.validate(missing_file)
        print("Missing file validation: PASS")

    print("\nAll document parser interface tests passed.")


if __name__ == "__main__":
    main()
