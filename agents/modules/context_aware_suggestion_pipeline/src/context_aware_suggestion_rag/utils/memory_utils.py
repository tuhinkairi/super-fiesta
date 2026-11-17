"""Memory monitoring and garbage collection utilities."""

from __future__ import annotations

import gc
import tracemalloc
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MemorySnapshot:
    """Snapshot of Python memory allocation statistics."""

    current_bytes: int
    peak_bytes: int
    tracing_active: bool

    @property
    def current_mb(self) -> float:
        return self.current_bytes / (1024 * 1024)

    @property
    def peak_mb(self) -> float:
        return self.peak_bytes / (1024 * 1024)


@dataclass(frozen=True, slots=True)
class GarbageCollectionResult:
    """Result of a garbage collection operation."""

    collected_objects: int
    generation: int
    before_counts: tuple[int, int, int]
    after_counts: tuple[int, int, int]

    @property
    def successful(self) -> bool:
        return self.collected_objects >= 0


def get_memory_snapshot() -> MemorySnapshot:
    """Return current and peak traced memory usage."""

    if not tracemalloc.is_tracing():
        return MemorySnapshot(
            current_bytes=0,
            peak_bytes=0,
            tracing_active=False,
        )

    current, peak = tracemalloc.get_traced_memory()

    return MemorySnapshot(
        current_bytes=current,
        peak_bytes=peak,
        tracing_active=True,
    )


def start_memory_tracking(
    *,
    nframe: int = 1,
    reset_peak: bool = False,
) -> bool:
    """Start memory tracking if it is not already active.

    Returns True if this call started tracking, otherwise False.
    """

    if isinstance(nframe, bool) or not isinstance(nframe, int):
        raise TypeError("nframe must be an integer.")

    if nframe <= 0:
        raise ValueError("nframe must be positive.")

    if not isinstance(reset_peak, bool):
        raise TypeError("reset_peak must be a boolean.")

    if tracemalloc.is_tracing():
        if reset_peak:
            tracemalloc.reset_peak()
        return False

    tracemalloc.start(nframe)
    return True


def stop_memory_tracking() -> bool:
    """Stop memory tracking if it is active."""

    if not tracemalloc.is_tracing():
        return False

    tracemalloc.stop()
    return True


def reset_memory_peak() -> bool:
    """Reset the traced memory peak to current usage."""

    if not tracemalloc.is_tracing():
        return False

    tracemalloc.reset_peak()
    return True


def get_garbage_collection_counts() -> tuple[int, int, int]:
    """Return garbage collection allocation counters."""

    counts = gc.get_count()
    return counts[0], counts[1], counts[2]


def get_garbage_collection_stats() -> list[dict[str, Any]]:
    """Return statistics for each garbage collection generation."""

    return [dict(item) for item in gc.get_stats()]


def collect_garbage(
    generation: int = 2,
) -> GarbageCollectionResult:
    """Collect unreachable objects in the requested generation."""

    if isinstance(generation, bool) or not isinstance(generation, int):
        raise TypeError("generation must be an integer.")

    if generation < 0 or generation > 2:
        raise ValueError("generation must be 0, 1, or 2.")

    before = get_garbage_collection_counts()
    collected = gc.collect(generation)
    after = get_garbage_collection_counts()

    return GarbageCollectionResult(
        collected_objects=collected,
        generation=generation,
        before_counts=before,
        after_counts=after,
    )


class MemoryTracker:
    """Manage a scoped memory-tracking session."""

    def __init__(self, nframe: int = 1) -> None:
        if isinstance(nframe, bool) or not isinstance(nframe, int):
            raise TypeError("nframe must be an integer.")

        if nframe <= 0:
            raise ValueError("nframe must be positive.")

        self.nframe = nframe
        self._started_tracking = False
        self._entered = False
        self._snapshot: MemorySnapshot | None = None

    def start(self) -> MemoryTracker:
        if self._entered:
            raise RuntimeError("Memory tracker is already active.")

        self._started_tracking = start_memory_tracking(
            nframe=self.nframe
        )
        self._entered = True
        self._snapshot = None

        return self

    def snapshot(self) -> MemorySnapshot:
        if not self._entered:
            raise RuntimeError("Memory tracker has not been started.")

        self._snapshot = get_memory_snapshot()
        return self._snapshot

    def stop(self) -> MemorySnapshot:
        if not self._entered:
            raise RuntimeError("Memory tracker has not been started.")

        result = get_memory_snapshot()

        if self._started_tracking:
            stop_memory_tracking()

        self._entered = False
        self._started_tracking = False
        self._snapshot = result

        return result

    def __enter__(self) -> MemoryTracker:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> bool:
        self.stop()
        return False

    @property
    def is_active(self) -> bool:
        return self._entered

    @property
    def last_snapshot(self) -> MemorySnapshot | None:
        return self._snapshot


__all__ = [
    "MemorySnapshot",
    "GarbageCollectionResult",
    "MemoryTracker",
    "get_memory_snapshot",
    "start_memory_tracking",
    "stop_memory_tracking",
    "reset_memory_peak",
    "get_garbage_collection_counts",
    "get_garbage_collection_stats",
    "collect_garbage",
]
