import argparse
import sys
from pathlib import Path

from modules.artist_graph_rag.src.graphrag_app.factory import create_application
from modules.artist_graph_rag.src.graphrag_app.ingestion import IngestionRequest
from modules.artist_graph_rag.src.graphrag_app.retrieval import RetrievalRequest


def positive_integer(value: str) -> int:
    """Validate positive integer CLI arguments."""

    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Value must be an integer.") from exc

    if number < 1:
        raise argparse.ArgumentTypeError("Value must be greater than zero.")

    return number


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""

    parser = argparse.ArgumentParser(
        prog="graphrag",
        description="Interact with the GraphRAG application.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # Document ingestion command.
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Process a document and store its knowledge graph.",
    )

    ingest_parser.add_argument(
        "file",
        type=Path,
        help="Path to a PDF, DOCX, or TXT document.",
    )

    # Question-answering command.
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a question using the knowledge graph.",
    )

    ask_parser.add_argument(
        "question",
        type=str,
        help="Question to ask.",
    )

    ask_parser.add_argument(
        "--top-k",
        type=positive_integer,
        default=10,
        help="Maximum number of matching entities.",
    )

    ask_parser.add_argument(
        "--document-id",
        type=str,
        default=None,
        help="Restrict retrieval to a particular document.",
    )

    # Database connection command.
    subparsers.add_parser(
        "check",
        help="Verify the Neo4j database connection.",
    )

    return parser


def run_ingestion(application, file_path: Path) -> int:
    """Process a document."""

    if not file_path.exists() or not file_path.is_file():
        print(
            f"Error: File not found: {file_path}",
            file=sys.stderr,
        )
        return 1

    request = IngestionRequest(
        filename=file_path.name,
        file_path=str(file_path.resolve()),
    )

    result = application.process_document(request)

    print(f"\nDocument: {result.filename}")
    print(f"Document ID: {result.document_id}")
    print(f"Status: {result.status.value}")
    print(f"Chunks created: {result.chunks_created}")
    print(f"Entities stored: {result.entities_stored}")
    print(f"Relationships stored: {result.relationships_stored}")

    if not result.success:
        print(
            f"Error: {result.error or result.message or 'Document processing failed.'}",
            file=sys.stderr,
        )
        return 1

    print(f"\n{result.message}")
    return 0


def run_question(
    application,
    question: str,
    top_k: int,
    document_id: str | None,
) -> int:
    """Retrieve knowledge and generate an answer."""

    request = RetrievalRequest(
        query=question,
        top_k=top_k,
        document_id=document_id,
    )

    retrieval_result, generation_result = application.ask(request)

    print("\n========== ANSWER ==========\n")
    print(generation_result.answer)

    print("\n======= RETRIEVAL INFO =======")
    print(f"Entities retrieved: {retrieval_result.total_entities}")
    print("Relationships retrieved: " f"{retrieval_result.total_relationships}")

    return 0


def main() -> int:
    """CLI application entry point."""

    parser = build_parser()
    args = parser.parse_args()

    try:
        with create_application() as application:

            if args.command == "check":
                connected = application.verify_database_connection()

                if connected:
                    print("Neo4j connection successful.")
                    return 0

                print(
                    "Neo4j connection failed.",
                    file=sys.stderr,
                )
                return 1

            if args.command == "ingest":
                return run_ingestion(
                    application,
                    args.file,
                )

            if args.command == "ask":
                return run_question(
                    application=application,
                    question=args.question,
                    top_k=args.top_k,
                    document_id=args.document_id,
                )

            return 1

    except Exception as error:
        print(
            f"Application error: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
