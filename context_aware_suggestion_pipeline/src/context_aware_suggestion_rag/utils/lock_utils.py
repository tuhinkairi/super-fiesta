
"""Thread synchronization and locking utilities."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from collections.abc import Iterator


class _ManagedRLock:
    """RLock wrapper that tracks ownership and acquisition state."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state_lock = threading.Lock()
        self._owner: int | None = None
        self._count = 0

    def acquire(self, blocking: bool = True, timeout: float = -1) -> bool:
        acquired = self._lock.acquire(blocking, timeout)

        if acquired:
            thread_id = threading.get_ident()

            with self._state_lock:
                if self._owner == thread_id:
                    self._count += 1
                else:
                    self._owner = thread_id
                    self._count = 1

        return acquired

    def release(self) -> None:
        thread_id = threading.get_ident()

        with self._state_lock:
            if self._owner != thread_id or self._count <= 0:
                raise RuntimeError("Lock is not owned by the current thread.")

            self._count -= 1

            if self._count == 0:
                self._owner = None

        self._lock.release()

    def is_locked(self) -> bool:
        with self._state_lock:
            return self._count > 0


class LockManager:
    """Manage named reentrant locks shared across application components."""

    def __init__(self) -> None:
        self._locks: dict[str, _ManagedRLock] = {}
        self._guard = threading.Lock()

    def get_lock(self, name: str) -> _ManagedRLock:
        if not isinstance(name, str):
            raise TypeError("name must be a string.")

        if not name.strip():
            raise ValueError("name cannot be empty.")

        with self._guard:
            if name not in self._locks:
                self._locks[name] = _ManagedRLock()

            return self._locks[name]

    def acquire(self, name: str, timeout: float = -1) -> bool:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric.")

        if timeout < -1:
            raise ValueError("timeout must be -1 or greater.")

        return self.get_lock(name).acquire(timeout=timeout)

    def release(self, name: str) -> None:
        self.get_lock(name).release()

    @contextmanager
    def locked(self, name: str, timeout: float = -1) -> Iterator[None]:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric.")

        if timeout < -1:
            raise ValueError("timeout must be -1 or greater.")

        lock = self.get_lock(name)
        acquired = lock.acquire(timeout=timeout)

        if not acquired:
            raise TimeoutError(f"Could not acquire lock: {name}")

        try:
            yield
        finally:
            lock.release()

    def remove_lock(self, name: str) -> bool:
        if not isinstance(name, str):
            raise TypeError("name must be a string.")

        with self._guard:
            lock = self._locks.get(name)

            if lock is None:
                return False

            if lock.is_locked():
                raise RuntimeError("Cannot remove an acquired lock.")

            del self._locks[name]
            return True

    def clear(self) -> None:
        with self._guard:
            if any(lock.is_locked() for lock in self._locks.values()):
                raise RuntimeError("Cannot clear locks while locks are acquired.")

            self._locks.clear()

    def __len__(self) -> int:
        with self._guard:
            return len(self._locks)


class ReadWriteLock:
    """Allow concurrent readers or one exclusive writer."""

    def __init__(self) -> None:
        self._condition = threading.Condition(threading.Lock())
        self._readers = 0
        self._writer_active = False
        self._waiting_writers = 0

    def acquire_read(self, timeout: float | None = None) -> bool:
        if timeout is not None:
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                raise TypeError("timeout must be numeric or None.")
            if timeout < 0:
                raise ValueError("timeout cannot be negative.")

        deadline = None if timeout is None else time.monotonic() + timeout

        with self._condition:
            while self._writer_active or self._waiting_writers > 0:
                if deadline is None:
                    self._condition.wait()
                else:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        return False
                    self._condition.wait(remaining)

            self._readers += 1
            return True

    def release_read(self) -> None:
        with self._condition:
            if self._readers <= 0:
                raise RuntimeError("No read lock is currently acquired.")

            self._readers -= 1

            if self._readers == 0:
                self._condition.notify_all()

    def acquire_write(self, timeout: float | None = None) -> bool:
        if timeout is not None:
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
                raise TypeError("timeout must be numeric or None.")
            if timeout < 0:
                raise ValueError("timeout cannot be negative.")

        deadline = None if timeout is None else time.monotonic() + timeout

        with self._condition:
            self._waiting_writers += 1

            try:
                while self._writer_active or self._readers > 0:
                    if deadline is None:
                        self._condition.wait()
                    else:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            return False
                        self._condition.wait(remaining)

                self._writer_active = True
                return True

            finally:
                self._waiting_writers -= 1

    def release_write(self) -> None:
        with self._condition:
            if not self._writer_active:
                raise RuntimeError("No write lock is currently acquired.")

            self._writer_active = False
            self._condition.notify_all()

    @contextmanager
    def read_lock(self, timeout: float | None = None) -> Iterator[None]:
        if not self.acquire_read(timeout):
            raise TimeoutError("Could not acquire read lock.")

        try:
            yield
        finally:
            self.release_read()

    @contextmanager
    def write_lock(self, timeout: float | None = None) -> Iterator[None]:
        if not self.acquire_write(timeout):
            raise TimeoutError("Could not acquire write lock.")

        try:
            yield
        finally:
            self.release_write()

    @property
    def reader_count(self) -> int:
        with self._condition:
            return self._readers

    @property
    def writer_active(self) -> bool:
        with self._condition:
            return self._writer_active


class ExecutionGuard:
    """Prevent overlapping execution of a protected operation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state_lock = threading.Lock()
        self._running = False

    def enter(self, blocking: bool = True) -> bool:
        if not isinstance(blocking, bool):
            raise TypeError("blocking must be a boolean.")

        acquired = self._lock.acquire(blocking=blocking)

        if acquired:
            with self._state_lock:
                self._running = True

        return acquired

    def exit(self) -> None:
        with self._state_lock:
            if not self._running:
                raise RuntimeError("Execution guard is not active.")

            self._running = False

        self._lock.release()

    @contextmanager
    def guard(self, blocking: bool = True) -> Iterator[bool]:
        acquired = self.enter(blocking=blocking)

        try:
            yield acquired
        finally:
            if acquired:
                self.exit()

    @property
    def is_running(self) -> bool:
        with self._state_lock:
            return self._running


__all__ = [
    "LockManager",
    "ReadWriteLock",
    "ExecutionGuard",
]
