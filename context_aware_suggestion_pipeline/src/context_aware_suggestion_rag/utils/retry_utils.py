"""Reusable retry utilities."""

from __future__ import annotations

import random
from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any, TypeVar

from tenacity import (
    RetryCallState,
    Retrying,
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

F = TypeVar("F", bound=Callable[..., Any])


def exponential_backoff(
    attempt: int,
    *,
    multiplier: float = 1.0,
    minimum: float = 0.0,
    maximum: float = 60.0,
    jitter: bool = False,
) -> float:
    """Calculate exponential backoff delay for an attempt."""
    if isinstance(attempt, bool) or not isinstance(attempt, int):
        raise TypeError("attempt must be an integer.")

    if attempt <= 0:
        raise ValueError("attempt must be greater than zero.")

    for name, value in (
        ("multiplier", multiplier),
        ("minimum", minimum),
        ("maximum", maximum),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be numeric.")

        if value < 0:
            raise ValueError(f"{name} must not be negative.")

    if maximum < minimum:
        raise ValueError("maximum must be greater than or equal to minimum.")

    if not isinstance(jitter, bool):
        raise TypeError("jitter must be a boolean.")

    delay = min(
        maximum,
        max(minimum, multiplier * (2 ** (attempt - 1))),
    )

    if jitter and delay > 0:
        delay = random.uniform(minimum, delay)

    return delay


def retry_call(
    function: Callable[..., Any],
    *args: Any,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    wait_multiplier: float = 1.0,
    wait_min: float = 0.0,
    wait_max: float = 10.0,
    **kwargs: Any,
) -> Any:
    """Execute a callable with configurable retries."""
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

    retryer = Retrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=wait_multiplier,
            min=wait_min,
            max=wait_max,
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
    )

    return retryer(
        lambda: function(*args, **kwargs)
    )


def retry(
    *,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    wait_multiplier: float = 1.0,
    wait_min: float = 0.0,
    wait_max: float = 10.0,
) -> Callable[[F], F]:
    """Decorate a synchronous function with retry behavior."""
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

    def decorator(function: F) -> F:
        if not callable(function):
            raise TypeError("Decorated object must be callable.")

        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return retry_call(
                function,
                *args,
                max_attempts=max_attempts,
                exceptions=exceptions,
                wait_multiplier=wait_multiplier,
                wait_min=wait_min,
                wait_max=wait_max,
                **kwargs,
            )

        return wrapper  # type: ignore[return-value]

    return decorator


def retrying_iterator(
    *,
    max_attempts: int = 3,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    wait_multiplier: float = 1.0,
    wait_min: float = 0.0,
    wait_max: float = 10.0,
) -> Retrying:
    """Create a configurable Tenacity retry iterator."""
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

    return Retrying(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=wait_multiplier,
            min=wait_min,
            max=wait_max,
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
    )


def retry_statistics(
    retry_state: RetryCallState,
) -> dict[str, Any]:
    """Extract useful statistics from a Tenacity retry state."""
    if not isinstance(retry_state, RetryCallState):
        raise TypeError("retry_state must be a RetryCallState.")

    outcome = retry_state.outcome
    exception_name = None
    succeeded = None

    if outcome is not None:
        succeeded = outcome.failed is False

        if outcome.failed:
            exception = outcome.exception()
            exception_name = (
                type(exception).__name__
                if exception is not None
                else None
            )

    return {
        "attempt_number": retry_state.attempt_number,
        "idle_for_seconds": retry_state.idle_for,
        "exception_name": exception_name,
        "succeeded": succeeded,
    }


__all__ = [
    "exponential_backoff",
    "retry_call",
    "retry",
    "retrying_iterator",
    "retry_statistics",
]
