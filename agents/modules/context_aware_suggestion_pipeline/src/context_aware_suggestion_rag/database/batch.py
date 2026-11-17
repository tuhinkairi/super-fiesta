"""Batch processing utilities for vector database operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.core.logging import get_logger
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.base import BaseVectorDatabase
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.database.models import (
    DatabaseOperationResult,
    VectorRecord,
)
from agents.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.exceptions import DatabaseError

logger = get_logger(__name__)


@dataclass
class BatchResult:
    """Summary of a batch database operation."""

    total_records: int
    successful_records: int = 0
    failed_records: int = 0
    batches_processed: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.failed_records == 0

    @property
    def success_rate(self) -> float:
        if self.total_records == 0:
            return 0.0

        return self.successful_records / self.total_records


class VectorBatchProcessor:
    """Process vector records in configurable batches."""

    def __init__(
        self,
        database: BaseVectorDatabase,
        batch_size: int = 100,
    ) -> None:
        if database is None:
            raise ValueError("A vector database instance is required.")

        if isinstance(batch_size, bool) or not isinstance(batch_size, int):
            raise TypeError("Batch size must be an integer.")

        if batch_size <= 0:
            raise ValueError("Batch size must be greater than zero.")

        self.database = database
        self.batch_size = batch_size

    def split_batches(
        self,
        records: Sequence[VectorRecord],
    ) -> list[list[VectorRecord]]:
        """Split records into smaller batches."""
        if not records:
            return []

        return [
            list(records[index:index + self.batch_size])
            for index in range(0, len(records), self.batch_size)
        ]

    def upsert_many(
        self,
        records: Sequence[VectorRecord],
    ) -> BatchResult:
        """Upsert records in batches and collect operation results."""
        result = BatchResult(total_records=len(records))

        if not records:
            return result

        batches = self.split_batches(records)

        for batch_number, batch in enumerate(batches, start=1):
            try:
                operation: DatabaseOperationResult = (
                    self.database.upsert(batch)
                )

                result.batches_processed += 1

                if operation.success:
                    result.successful_records += operation.affected_count
                else:
                    result.failed_records += len(batch)
                    result.errors.append(
                        operation.message
                        or f"Batch {batch_number} failed."
                    )

            except Exception as exc:
                result.failed_records += len(batch)
                result.errors.append(
                    f"Batch {batch_number}: {exc}"
                )

                logger.exception(
                    "Vector batch %s failed.",
                    batch_number,
                )

        # Account for any mismatch in reported affected counts.
        accounted = (
            result.successful_records + result.failed_records
        )

        if accounted < result.total_records:
            result.failed_records += result.total_records - accounted

        return result
