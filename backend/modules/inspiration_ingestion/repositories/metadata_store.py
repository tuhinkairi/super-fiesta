import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from modules.inspiration_ingestion.config import (
    get_inspiration_settings,
)

from modules.inspiration_ingestion.types import (
    InspirationRecord,
)


class MetadataStore:
    """
    Stores and retrieves inspiration metadata using SQLite.
    """

    def __init__(self, db_path: str | Path | None = None):

        settings = get_inspiration_settings()

        self.db_path = Path(
            db_path if db_path is not None else settings.storage_dir / "inspiration.db"
        )

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        """
        Open and safely close a database connection.
        """

        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        try:
            yield connection
            connection.commit()

        except Exception:
            connection.rollback()
            raise

        finally:
            connection.close()

    def _initialize_database(self):
        """
        Create the inspiration table if it does not exist.
        """

        with self._connection() as connection:

            connection.execute("""
                CREATE TABLE IF NOT EXISTS inspirations (
                    id TEXT PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    source TEXT,
                    storage_path TEXT,
                    uploaded_at TEXT NOT NULL,
                    extracted_text TEXT,
                    summary TEXT,
                    description TEXT,
                    keywords TEXT,
                    themes TEXT,
                    mood_tags TEXT,
                    provenance TEXT,
                    embedding TEXT
                )
                """)

    def save(self, record: InspirationRecord) -> None:
        """
        Save an inspiration record.
        Update it if the same ID already exists.
        """

        data = record.model_dump(mode="json")

        with self._connection() as connection:

            connection.execute(
                """
                INSERT INTO inspirations (
                    id,
                    file_name,
                    content_type,
                    source,
                    storage_path,
                    uploaded_at,
                    extracted_text,
                    summary,
                    description,
                    keywords,
                    themes,
                    mood_tags,
                    provenance,
                    embedding
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(id) DO UPDATE SET
                    file_name = excluded.file_name,
                    content_type = excluded.content_type,
                    source = excluded.source,
                    storage_path = excluded.storage_path,
                    uploaded_at = excluded.uploaded_at,
                    extracted_text = excluded.extracted_text,
                    summary = excluded.summary,
                    description = excluded.description,
                    keywords = excluded.keywords,
                    themes = excluded.themes,
                    mood_tags = excluded.mood_tags,
                    provenance = excluded.provenance,
                    embedding = excluded.embedding
                """,
                (
                    data["id"],
                    data["file_name"],
                    data["content_type"],
                    data["source"],
                    data["storage_path"],
                    data["uploaded_at"],
                    data["extracted_text"],
                    data["summary"],
                    data["description"],
                    json.dumps(data["keywords"]),
                    json.dumps(data["themes"]),
                    json.dumps(data["mood_tags"]),
                    json.dumps(data["provenance"]),
                    (
                        json.dumps(data["embedding"])
                        if data["embedding"] is not None
                        else None
                    ),
                ),
            )

    def get(self, record_id: str) -> InspirationRecord | None:
        """
        Retrieve one inspiration record by ID.
        """

        with self._connection() as connection:

            row = connection.execute(
                """
                SELECT * FROM inspirations
                WHERE id = ?
                """,
                (record_id,),
            ).fetchone()

        if row is None:
            return None

        data = dict(row)

        # Convert JSON database fields back into Python objects.
        for field in (
            "keywords",
            "themes",
            "mood_tags",
            "provenance",
        ):
            data[field] = json.loads(data[field])

        if data["embedding"] is not None:
            data["embedding"] = json.loads(data["embedding"])

        return InspirationRecord.model_validate(data)

    def get_all(self) -> list[InspirationRecord]:
        """
        Retrieve all stored inspiration records.
        """

        with self._connection() as connection:

            rows = connection.execute("""
                SELECT id FROM inspirations
                ORDER BY uploaded_at DESC
                """).fetchall()

        records = []

        for row in rows:
            record = self.get(row["id"])

            if record is not None:
                records.append(record)

        return records

    def count(self) -> int:
        """
        Return the total number of stored records.
        """

        with self._connection() as connection:

            result = connection.execute("SELECT COUNT(*) FROM inspirations").fetchone()

        return result[0]
