
import gc
import tracemalloc

from context_aware_suggestion_rag.utils.memory_utils import (
    GarbageCollectionResult,
    MemorySnapshot,
    MemoryTracker,
    collect_garbage,
    get_garbage_collection_counts,
    get_garbage_collection_stats,
    get_memory_snapshot,
    reset_memory_peak,
    start_memory_tracking,
    stop_memory_tracking,
)


def cleanup_tracing():
    if tracemalloc.is_tracing():
        tracemalloc.stop()


def test_memory_snapshot_without_tracking():
    cleanup_tracing()

    snapshot = get_memory_snapshot()

    assert isinstance(snapshot, MemorySnapshot)
    assert snapshot.tracing_active is False
    assert snapshot.current_bytes == 0
    assert snapshot.peak_bytes == 0


def test_start_and_stop_tracking():
    cleanup_tracing()

    try:
        assert start_memory_tracking() is True
        assert tracemalloc.is_tracing()

        # A second start must not restart the existing session.
        assert start_memory_tracking() is False

        snapshot = get_memory_snapshot()

        assert snapshot.tracing_active is True
        assert snapshot.current_bytes >= 0
        assert snapshot.peak_bytes >= snapshot.current_bytes

        assert stop_memory_tracking() is True
        assert tracemalloc.is_tracing() is False

        assert stop_memory_tracking() is False
    finally:
        cleanup_tracing()


def test_reset_memory_peak():
    cleanup_tracing()

    try:
        start_memory_tracking()

        allocation = bytearray(100_000)
        assert len(allocation) == 100_000

        assert reset_memory_peak() is True

        snapshot = get_memory_snapshot()
        assert snapshot.peak_bytes >= snapshot.current_bytes

        del allocation
    finally:
        cleanup_tracing()


def test_garbage_collection_counts():
    counts = get_garbage_collection_counts()

    assert isinstance(counts, tuple)
    assert len(counts) == 3
    assert all(isinstance(value, int) for value in counts)


def test_garbage_collection_stats():
    stats = get_garbage_collection_stats()

    assert isinstance(stats, list)
    assert len(stats) == 3
    assert all(isinstance(item, dict) for item in stats)


def test_collect_garbage():
    result = collect_garbage()

    assert isinstance(result, GarbageCollectionResult)
    assert result.generation == 2
    assert result.collected_objects >= 0
    assert len(result.before_counts) == 3
    assert len(result.after_counts) == 3


def test_collect_specific_generation():
    for generation in range(3):
        result = collect_garbage(generation)
        assert result.generation == generation


def test_invalid_generation():
    for generation in (-1, 3, True):
        try:
            collect_garbage(generation)
            assert False, "Expected validation error"
        except (TypeError, ValueError):
            pass


def test_memory_tracker_context_manager():
    cleanup_tracing()

    try:
        with MemoryTracker() as tracker:
            assert tracker.is_active
            assert tracemalloc.is_tracing()

            allocation = bytearray(50_000)
            snapshot = tracker.snapshot()

            assert snapshot.tracing_active
            assert snapshot.current_bytes > 0
            assert len(allocation) == 50_000

        assert not tracker.is_active
        assert not tracemalloc.is_tracing()
        assert tracker.last_snapshot is not None
        assert tracker.last_snapshot.tracing_active

    finally:
        cleanup_tracing()


def test_tracker_preserves_existing_session():
    cleanup_tracing()

    try:
        start_memory_tracking()

        with MemoryTracker() as tracker:
            assert tracker.is_active
            assert tracemalloc.is_tracing()

        # The tracker did not start the session, so it must not stop it.
        assert tracemalloc.is_tracing()
        assert tracker.last_snapshot is not None

    finally:
        cleanup_tracing()


if __name__ == "__main__":
    tests = [
        test_memory_snapshot_without_tracking,
        test_start_and_stop_tracking,
        test_reset_memory_peak,
        test_garbage_collection_counts,
        test_garbage_collection_stats,
        test_collect_garbage,
        test_collect_specific_generation,
        test_invalid_generation,
        test_memory_tracker_context_manager,
        test_tracker_preserves_existing_session,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All memory utility tests passed.")
