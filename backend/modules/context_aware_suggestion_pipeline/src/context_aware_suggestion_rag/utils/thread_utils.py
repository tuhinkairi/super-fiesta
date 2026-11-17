"""Threading and concurrent execution utilities."""

from __future__ import annotations

import threading
from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
    as_completed,
)
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class ThreadTaskResult:
    """Result of an individual threaded task."""

    task_index: int
    success: bool
    result: Any = None
    error: str | None = None

    def __post_init__(self) -> None:
        if isinstance(self.task_index, bool) or not isinstance(
            self.task_index, int
        ):
            raise TypeError("task_index must be an integer.")

        if self.task_index < 0:
            raise ValueError("task_index cannot be negative.")

        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean.")

        if self.error is not None and not isinstance(self.error, str):
            raise TypeError("error must be a string or None.")


def get_thread_count() -> int:
    """Return the number of active threads."""
    return threading.active_count()


def get_current_thread_name() -> str:
    """Return the current thread's name."""
    return threading.current_thread().name


def get_current_thread_id() -> int:
    """Return the current thread identifier."""
    return threading.get_ident()


def is_main_thread() -> bool:
    """Check whether the current thread is the main thread."""
    return threading.current_thread() is threading.main_thread()


def create_thread(
    target: Callable[..., Any],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    name: str | None = None,
    daemon: bool = False,
) -> threading.Thread:
    """Create a thread without starting it."""
    if not callable(target):
        raise TypeError("target must be callable.")

    if not isinstance(args, tuple):
        raise TypeError("args must be a tuple.")

    if kwargs is None:
        kwargs = {}

    if not isinstance(kwargs, dict):
        raise TypeError("kwargs must be a dictionary.")

    if name is not None and not isinstance(name, str):
        raise TypeError("name must be a string or None.")

    if not isinstance(daemon, bool):
        raise TypeError("daemon must be a boolean.")

    return threading.Thread(
        target=target,
        args=args,
        kwargs=kwargs,
        name=name,
        daemon=daemon,
    )


def start_thread(
    target: Callable[..., Any],
    *,
    args: tuple[Any, ...] = (),
    kwargs: dict[str, Any] | None = None,
    name: str | None = None,
    daemon: bool = False,
) -> threading.Thread:
    """Create and immediately start a thread."""
    thread = create_thread(
        target,
        args=args,
        kwargs=kwargs,
        name=name,
        daemon=daemon,
    )

    thread.start()
    return thread


def join_thread(
    thread: threading.Thread,
    timeout: float | None = None,
) -> bool:
    """Wait for a thread to finish and report whether it stopped."""
    if not isinstance(thread, threading.Thread):
        raise TypeError("thread must be a threading.Thread.")

    if timeout is not None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric or None.")

        if timeout < 0:
            raise ValueError("timeout cannot be negative.")

    if thread.ident is None:
        raise RuntimeError("Cannot join a thread that has not been started.")

    if thread is threading.current_thread():
        raise RuntimeError("A thread cannot join itself.")

    thread.join(timeout=timeout)
    return not thread.is_alive()


def run_in_thread_pool(
    function: Callable[..., T],
    tasks: Iterable[tuple[tuple[Any, ...], dict[str, Any]]],
    *,
    max_workers: int | None = None,
) -> list[T]:
    """Execute function calls concurrently and preserve input order."""
    if not callable(function):
        raise TypeError("function must be callable.")

    if max_workers is not None:
        if isinstance(max_workers, bool) or not isinstance(max_workers, int):
            raise TypeError("max_workers must be an integer or None.")

        if max_workers <= 0:
            raise ValueError("max_workers must be greater than zero.")

    task_list = list(tasks)

    for task in task_list:
        if not isinstance(task, tuple) or len(task) != 2:
            raise TypeError(
                "Each task must be a tuple of (args, kwargs)."
            )

        args, kwargs = task

        if not isinstance(args, tuple):
            raise TypeError("Task args must be a tuple.")

        if not isinstance(kwargs, dict):
            raise TypeError("Task kwargs must be a dictionary.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(function, *args, **kwargs)
            for args, kwargs in task_list
        ]

        return [future.result() for future in futures]


def run_tasks_with_results(
    tasks: Sequence[Callable[[], T]],
    *,
    max_workers: int | None = None,
) -> list[ThreadTaskResult]:
    """Execute task callables and collect individual successes and failures."""
    if not isinstance(tasks, Sequence):
        raise TypeError("tasks must be a sequence.")

    if isinstance(tasks, (str, bytes, bytearray)):
        raise TypeError("tasks must contain callables.")

    if any(not callable(task) for task in tasks):
        raise TypeError("Every task must be callable.")

    if max_workers is not None:
        if isinstance(max_workers, bool) or not isinstance(max_workers, int):
            raise TypeError("max_workers must be an integer or None.")

        if max_workers <= 0:
            raise ValueError("max_workers must be greater than zero.")

    results: list[ThreadTaskResult | None] = [None] * len(tasks)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index: dict[Future[Any], int] = {
            executor.submit(task): index
            for index, task in enumerate(tasks)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]

            try:
                results[index] = ThreadTaskResult(
                    task_index=index,
                    success=True,
                    result=future.result(),
                )
            except Exception as exc:
                results[index] = ThreadTaskResult(
                    task_index=index,
                    success=False,
                    error=f"{type(exc).__name__}: {exc}",
                )

    return [
        result
        for result in results
        if result is not None
    ]


class ThreadSafeCounter:
    """A simple thread-safe integer counter."""

    def __init__(self, initial_value: int = 0) -> None:
        if isinstance(initial_value, bool) or not isinstance(
            initial_value, int
        ):
            raise TypeError("initial_value must be an integer.")

        self._value = initial_value
        self._lock = threading.Lock()

    def increment(self, amount: int = 1) -> int:
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer.")

        with self._lock:
            self._value += amount
            return self._value

    def decrement(self, amount: int = 1) -> int:
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError("amount must be an integer.")

        with self._lock:
            self._value -= amount
            return self._value

    def get(self) -> int:
        with self._lock:
            return self._value

    def reset(self, value: int = 0) -> None:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("value must be an integer.")

        with self._lock:
            self._value = value


__all__ = [
    "ThreadTaskResult",
    "get_thread_count",
    "get_current_thread_name",
    "get_current_thread_id",
    "is_main_thread",
    "create_thread",
    "start_thread",
    "join_thread",
    "run_in_thread_pool",
    "run_tasks_with_results",
    "ThreadSafeCounter",
]
