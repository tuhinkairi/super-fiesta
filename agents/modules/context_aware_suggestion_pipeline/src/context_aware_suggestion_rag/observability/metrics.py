"""In-memory metrics collection provider."""

from __future__ import annotations

from collections import defaultdict
from threading import RLock

from .base import BaseMetricsProvider
from .models import MetricRecord, MetricType, current_utc_time


class InMemoryMetricsProvider(BaseMetricsProvider):
    """Thread-safe in-memory metrics provider."""

    def __init__(self, max_records: int = 10000) -> None:
        if (
            isinstance(max_records, bool)
            or not isinstance(max_records, int)
            or max_records <= 0
        ):
            raise ValueError("max_records must be a positive integer.")

        self.max_records = max_records
        self._metrics: list[MetricRecord] = []
        self._counters: dict[tuple[str, tuple[tuple[str, str], ...]], float] = (
            defaultdict(float)
        )
        self._lock = RLock()
        self._connected = False
        self._closed = False

    def connect(self) -> None:
        """Initialize the metrics provider."""
        with self._lock:
            if self._closed:
                raise RuntimeError("Metrics provider is closed.")
            self._connected = True

    def health_check(self) -> bool:
        """Check provider availability."""
        with self._lock:
            return self._connected and not self._closed

    def _ensure_connected(self) -> None:
        if self._closed:
            raise RuntimeError("Metrics provider is closed.")

        if not self._connected:
            self.connect()

    @staticmethod
    def _validate_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Metric name must be a non-empty string.")
        return name.strip()

    @staticmethod
    def _validate_value(value: float) -> float:
        from math import isfinite

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Metric value must be numeric.")

        result = float(value)

        if not isfinite(result):
            raise ValueError("Metric value must be finite.")

        return result

    @staticmethod
    def _normalize_labels(
        labels: dict[str, str] | None,
    ) -> dict[str, str]:
        if labels is None:
            return {}

        if not isinstance(labels, dict):
            raise TypeError("Metric labels must be a dictionary.")

        normalized: dict[str, str] = {}

        for key, value in labels.items():
            if not isinstance(key, str) or not key.strip():
                raise ValueError("Metric label keys must be non-empty strings.")

            if not isinstance(value, str):
                raise TypeError("Metric label values must be strings.")

            normalized[key.strip()] = value

        return normalized

    def _record(
        self,
        name: str,
        metric_type: MetricType,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        self._ensure_connected()

        record = MetricRecord(
            name=name,
            metric_type=metric_type,
            value=value,
            labels=self._normalize_labels(labels),
            timestamp=current_utc_time(),
        )

        with self._lock:
            self._metrics.append(record)

            if len(self._metrics) > self.max_records:
                del self._metrics[: len(self._metrics) - self.max_records]

        return record

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Increment and record a counter."""
        name = self._validate_name(name)
        value = self._validate_value(value)
        normalized_labels = self._normalize_labels(labels)

        if value < 0:
            raise ValueError("Counter increments cannot be negative.")

        label_key = tuple(sorted(normalized_labels.items()))
        counter_key = (name, label_key)

        self._ensure_connected()

        with self._lock:
            self._counters[counter_key] += value
            total = self._counters[counter_key]

        return self._record(
            name=name,
            metric_type=MetricType.COUNTER,
            value=total,
            labels=normalized_labels,
        )

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Record a gauge value."""
        return self._record(
            name=self._validate_name(name),
            metric_type=MetricType.GAUGE,
            value=self._validate_value(value),
            labels=labels,
        )

    def timing(
        self,
        name: str,
        duration_ms: float,
        labels: dict[str, str] | None = None,
    ) -> MetricRecord:
        """Record an operation duration in milliseconds."""
        duration = self._validate_value(duration_ms)

        if duration < 0:
            raise ValueError("Timing duration cannot be negative.")

        return self._record(
            name=self._validate_name(name),
            metric_type=MetricType.TIMING,
            value=duration,
            labels=labels,
        )

    def get_metrics(
        self,
        name: str | None = None,
    ) -> list[MetricRecord]:
        """Return metric records, optionally filtered by name."""
        self._ensure_connected()

        if name is not None:
            name = self._validate_name(name)

        with self._lock:
            records = list(self._metrics)

        if name is not None:
            records = [record for record in records if record.name == name]

        return records

    def get_counter_value(
        self,
        name: str,
        labels: dict[str, str] | None = None,
    ) -> float:
        """Return the current counter value for a name and label set."""
        name = self._validate_name(name)
        normalized_labels = self._normalize_labels(labels)
        label_key = tuple(sorted(normalized_labels.items()))

        with self._lock:
            return self._counters.get((name, label_key), 0.0)

    def clear(self) -> None:
        """Clear all recorded metrics and counter values."""
        self._ensure_connected()

        with self._lock:
            self._metrics.clear()
            self._counters.clear()

    def close(self) -> None:
        """Close the metrics provider."""
        with self._lock:
            self._connected = False
            self._closed = True
