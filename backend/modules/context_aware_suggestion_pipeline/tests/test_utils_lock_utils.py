
import threading
import time

from context_aware_suggestion_rag.utils.lock_utils import (
    ExecutionGuard,
    LockManager,
    ReadWriteLock,
)

def test_lock_manager():
    manager = LockManager()

    lock_a = manager.get_lock("database")
    lock_b = manager.get_lock("database")

    assert lock_a is lock_b
    assert len(manager) == 1

    with manager.locked("database"):
        # RLock is reentrant: acquiring it again in this thread succeeds.
        assert lock_a.acquire(blocking=False)
        lock_a.release()

    assert manager.remove_lock("database") is True
    assert len(manager) == 0

def test_lock_timeout():
    manager = LockManager()
    lock = manager.get_lock("test")

    acquired = threading.Event()
    release = threading.Event()

    def hold_lock():
        lock.acquire()
        acquired.set()

        try:
            release.wait(timeout=2)
        finally:
            lock.release()

    thread = threading.Thread(target=hold_lock)
    thread.start()

    try:
        assert acquired.wait(timeout=1)
        assert manager.acquire("test", timeout=0.05) is False
    finally:
        release.set()
        thread.join(timeout=2)

    assert not thread.is_alive()


def test_read_write_lock():
    lock = ReadWriteLock()

    assert lock.acquire_read(timeout=1)
    assert lock.acquire_read(timeout=1)
    assert lock.reader_count == 2

    lock.release_read()
    lock.release_read()

    assert lock.reader_count == 0

    assert lock.acquire_write(timeout=1)
    assert lock.writer_active

    lock.release_write()
    assert not lock.writer_active


def test_writer_excludes_reader():
    lock = ReadWriteLock()
    assert lock.acquire_write(timeout=1)

    result = {"acquired": None}

    def reader():
        result["acquired"] = lock.acquire_read(timeout=0.05)

        if result["acquired"]:
            lock.release_read()

    thread = threading.Thread(target=reader)
    thread.start()
    thread.join(timeout=2)

    lock.release_write()

    assert result["acquired"] is False


def test_execution_guard():
    guard = ExecutionGuard()

    with guard.guard() as acquired:
        assert acquired is True
        assert guard.is_running is True

        assert guard.enter(blocking=False) is False

    assert guard.is_running is False


def test_execution_guard_non_blocking():
    guard = ExecutionGuard()

    assert guard.enter(blocking=False) is True
    assert guard.enter(blocking=False) is False

    guard.exit()

    assert guard.is_running is False


if __name__ == "__main__":
    tests = [
        test_lock_manager,
        test_lock_timeout,
        test_read_write_lock,
        test_writer_excludes_reader,
        test_execution_guard,
        test_execution_guard_non_blocking,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All lock utility tests passed.")
