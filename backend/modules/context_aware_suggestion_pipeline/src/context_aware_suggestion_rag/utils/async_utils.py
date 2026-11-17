"""Reusable asynchronous programming utilities."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Awaitable, Callable, Iterable, Sequence
from functools import wraps
from typing import Any, TypeVar

from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


async def run_with_timeout(
    awaitable: Awaitable[T],
    timeout: float,
    *,
    default: T | None = None,
    raise_on_timeout: bool = True,
) -> T | None:
    """Execute an awaitable with a timeout."""
    if not inspect.isawaitable(awaitable):
        raise TypeError("awaitable must be awaitable.")

    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        raise TypeError("timeout must be numeric.")

    if timeout <= 0:
        raise ValueError("timeout must be greater than zero.")

    if not isinstance(raise_on_timeout, bool):
        raise TypeError("raise_on_timeout must be a boolean.")

    try:
        return await asyncio.wait_for(awaitable, timeout=float(timeout))
    except asyncio.TimeoutError:
        if raise_on_timeout:
            raise
        return default


async def retry_async_call(
    function: Callable[..., Awaitable[T]],
    *args: Any,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    wait_multiplier: float = 1.0,
    wait_min: float = 0.0,
    wait_max: float = 10.0,
    **kwargs: Any,
) -> T:
    """Execute an asynchronous callable with retries."""
    if not callable(function):
        raise TypeError("function must be callable.")

    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise TypeError("max_attempts must be an integer.")

    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero.")

    if (
        not isinstance(exceptions, tuple)
        or not exceptions
        or any(
            not isinstance(exception, type)
            or not issubclass(exception, BaseException)
            for exception in exceptions
        )
    ):
        raise TypeError("exceptions must be a non-empty tuple of exception types.")

    async for attempt in AsyncRetrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=wait_multiplier,
            min=wait_min,
            max=wait_max,
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
    ):
        with attempt:
            result = function(*args, **kwargs)

            if not inspect.isawaitable(result):
                raise TypeError("The supplied function must return an awaitable.")

            return await result

    raise RuntimeError("Asynchronous retry operation ended unexpectedly.")


def async_retry(
    *,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    wait_multiplier: float = 1.0,
    wait_min: float = 0.0,
    wait_max: float = 10.0,
):
    """Decorate an asynchronous function with retry behavior."""
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise TypeError("max_attempts must be an integer.")

    if max_attempts <= 0:
        raise ValueError("max_attempts must be greater than zero.")

    if (
        not isinstance(exceptions, tuple)
        or not exceptions
        or any(
            not isinstance(exception, type)
            or not issubclass(exception, BaseException)
            for exception in exceptions
        )
    ):
        raise TypeError("exceptions must be a non-empty tuple of exception types.")

    def decorator(function: Callable[..., Awaitable[T]]):
        if not callable(function):
            raise TypeError("Decorated object must be callable.")

        if not inspect.iscoroutinefunction(function):
            raise TypeError("async_retry can only decorate async functions.")

        @wraps(function)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await retry_async_call(
                function,
                *args,
                max_attempts=max_attempts,
                exceptions=exceptions,
                wait_multiplier=wait_multiplier,
                wait_min=wait_min,
                wait_max=wait_max,
                **kwargs,
            )

        return wrapper

    return decorator


async def gather_with_concurrency(
    awaitables: Iterable[Awaitable[T]],
    *,
    limit: int,
        return_exceptions: bool = False,
) -> list[T | BaseException]:
    """Run awaitables concurrently with a maximum concurrency limit."""
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError("limit must be an integer.")

    if limit <= 0:
        raise ValueError("limit must be greater than zero.")

    if not isinstance(return_exceptions, bool):
        raise TypeError("return_exceptions must be a boolean.")

    tasks = list(awaitables)

    if any(not inspect.isawaitable(task) for task in tasks):
        raise TypeError("Every item must be awaitable.")

    semaphore = asyncio.Semaphore(limit)

    async def execute(awaitable: Awaitable[T]) -> T:
        async with semaphore:
            return await awaitable

    return await asyncio.gather(
        *(execute(task) for task in tasks),
        return_exceptions=return_exceptions,
    )


async def run_tasks(
    tasks: Sequence[Callable[[], Awaitable[T]]],
    *,
    limit: int | None = None,
    return_exceptions: bool = False,
) -> list[T | BaseException]:
    """Execute a sequence of asynchronous task factories."""
    if not isinstance(tasks, Sequence):
        raise TypeError("tasks must be a sequence.")

    if isinstance(tasks, (str, bytes, bytearray)):
        raise TypeError("tasks must be a sequence of callables.")

    if not isinstance(return_exceptions, bool):
        raise TypeError("return_exceptions must be a boolean.")

    if any(not callable(task) for task in tasks):
        raise TypeError("Every task must be callable.")

    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer or None.")

        if limit <= 0:
            raise ValueError("limit must be greater than zero.")

    semaphore = asyncio.Semaphore(limit) if limit is not None else None

    async def execute(factory: Callable[[], Awaitable[T]]) -> T:
        if semaphore is None:
            result = factory()
            if not inspect.isawaitable(result):
                raise TypeError("Every task factory must return an awaitable.")
            return await result

        async with semaphore:
            result = factory()
            if not inspect.isawaitable(result):
                raise TypeError("Every task factory must return an awaitable.")
            return await result

    return await asyncio.gather(
        *(execute(task) for task in tasks),
        return_exceptions=return_exceptions,
    )


async def cancel_tasks(
    tasks: Iterable[asyncio.Task[Any]],
) -> int:
    """Cancel unfinished asyncio tasks and wait for their completion."""
    task_list = list(tasks)

    if any(not isinstance(task, asyncio.Task) for task in task_list):
        raise TypeError("Every item must be an asyncio.Task.")

    pending = [task for task in task_list if not task.done()]

    for task in pending:
        task.cancel()

    if pending:
        await asyncio.gather(*pending, return_exceptions=True)

    return len(pending)


async def wait_for_tasks(
    tasks: Iterable[asyncio.Task[T]],
    *,
    timeout: float | None = None,
) -> tuple[set[asyncio.Task[T]], set[asyncio.Task[T]]]:
    """Wait for tasks and return completed and pending sets."""
    task_list = list(tasks)

    if any(not isinstance(task, asyncio.Task) for task in task_list):
        raise TypeError("Every item must be an asyncio.Task.")

    if timeout is not None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric or None.")

        if timeout < 0:
            raise ValueError("timeout must not be negative.")

    done, pending = await asyncio.wait(
        task_list,
        timeout=timeout,
        return_when=asyncio.ALL_COMPLETED,
    )

    return done, pending


__all__ = [
    "run_with_timeout",
    "retry_async_call",
    "async_retry",
    "gather_with_concurrency",
    "run_tasks",
    "cancel_tasks",
    "wait_for_tasks",
]
