"""
Reusable retry utilities.

Provides configurable retry decorators for operations that may
fail temporarily due to network errors, rate limits, or service
availability issues.
"""

import logging
from typing import Any, Callable, ParamSpec, TypeVar, cast

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("context_aware_suggestion_rag.retry")


def retry_operation(
    *,
    attempts: int = 3,
    min_wait_seconds: float = 1.0,
    max_wait_seconds: float = 10.0,
    multiplier: float = 1.0,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Create a retry decorator for an operation.

    Tenacity automatically supports both synchronous and asynchronous
    functions through its retry decorator.

    Args:
        attempts: Maximum number of attempts, including the first call.
        min_wait_seconds: Minimum exponential backoff delay.
        max_wait_seconds: Maximum exponential backoff delay.
        multiplier: Exponential backoff multiplier.
        exceptions: Exception types that should trigger a retry.

    Returns:
        A decorator that retries the decorated operation.

    Raises:
        ValueError: If retry configuration is invalid.
    """

    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    if min_wait_seconds < 0:
        raise ValueError("min_wait_seconds cannot be negative")

    if max_wait_seconds < min_wait_seconds:
        raise ValueError(
            "max_wait_seconds must be greater than or equal to "
            "min_wait_seconds"
        )

    if multiplier <= 0:
        raise ValueError("multiplier must be greater than 0")

    if not exceptions:
        raise ValueError("At least one exception type must be provided")

    for exception_type in exceptions:
        if not isinstance(exception_type, type) or not issubclass(
            exception_type, BaseException
        ):
            raise TypeError(
                "exceptions must contain exception classes"
            )

    decorator = retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(
            multiplier=multiplier,
            min=min_wait_seconds,
            max=max_wait_seconds,
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
        before_sleep=lambda retry_state: logger.warning(
            "Operation failed. Retrying attempt %s/%s after %.2f seconds.",
            retry_state.attempt_number,
            attempts,
            retry_state.next_action.sleep
            if retry_state.next_action
            else 0.0,
        ),
    )

    return cast(Callable[[Callable[P, R]], Callable[P, R]], decorator)


__all__ = ["retry_operation"]
