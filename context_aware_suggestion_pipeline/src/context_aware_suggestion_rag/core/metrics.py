"""
Centralized metrics collection.

Provides thread-safe counters and timing measurements for
monitoring pipeline operations.
"""

from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from threading import Lock
from time import perf_counter
from typing import Iterator, Mapping


@dataclass(frozen=True, slots=True)
class MetricsSnapshot:
    """Immutable snapshot of collected metrics."""

    counters: dict[str, int]
    timings: dict[str, tuple[float, ...]]


class MetricsCollector:
    """
    Collect counters and execution timings safely across threads.

    This collector stores metrics in memory. It does not send
    telemetry to an external monitoring service.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def increment(
        self,
        name: str,
        value: int = 1,
    ) -> None:
        """Increment a named counter."""

        self._validate_name(name)

        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("Counter increment must be an integer")

        if value < 0:
            raise ValueError("Counter increment cannot be negative")

        with self._lock:
            self._counters[name] += value

    def record_timing(
        self,
        name: str,
        duration_seconds: float,
    ) -> None:
        """Record an execution duration in seconds."""

        self._validate_name(name)

        if isinstance(duration_seconds, bool) or not isinstance(
            duration_seconds, (int, float)
        ):
            raise TypeError("Duration must be a number")

        if duration_seconds < 0:
            raise ValueError("Duration cannot be negative")

        with self._lock:
            self._timings[name].append(float(duration_seconds))

    @contextmanager
    def measure(self, name: str) -> Iterator[None]:
        """
        Measure the execution time of a code block.

        Example:
            with metrics.measure("document_processing"):
                process_document()
        """

        self._validate_name(name)
        start_time = perf_counter()

        try:
            yield
        finally:
            elapsed = perf_counter() - start_time
            self.record_timing(name, elapsed)

    def get_snapshot(self) -> MetricsSnapshot:
        """Return a consistent snapshot of all collected metrics."""

        with self._lock:
            return MetricsSnapshot(
                counters=dict(self._counters),
                timings={
                    name: tuple(values)
                    for name, values in self._timings.items()
                },
            )

    def get_counter(self, name: str) -> int:
        """Return the current value of a counter."""

        self._validate_name(name)

        with self._lock:
            return self._counters.get(name, 0)

    def get_average_timing(self, name: str) -> float | None:
        """Return the average duration for a timing metric."""

        self._validate_name(name)

        with self._lock:
            values = self._timings.get(name)

            if not values:
                return None

            return sum(values) / len(values)

    def reset(self) -> None:
        """Clear all collected metrics."""

        with self._lock:
            self._counters.clear()
            self._timings.clear()

    @staticmethod
    def _validate_name(name: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Metric name must be a non-empty string")


# Shared collector for package-wide metrics.
metrics = MetricsCollector()


__all__ = [
    "MetricsSnapshot",
    "MetricsCollector",
    "metrics",
]
