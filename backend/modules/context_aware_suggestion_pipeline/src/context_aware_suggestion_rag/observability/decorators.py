"""Decorators for automatic application observability."""

from __future__ import annotations

import inspect
from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar

from .monitoring import ApplicationMonitor


F = TypeVar("F", bound=Callable[..., Any])


def _build_execution_id(function_name: str) -> str:
    """Generate a lightweight execution identifier."""
    from uuid import uuid4

    return f"{function_name}_{uuid4().hex[:12]}"


def _resolve_monitor(
    monitor: ApplicationMonitor | None,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> ApplicationMonitor | None:
    """Resolve a monitor from explicit input or the decorated object."""
    if monitor is not None:
        return monitor

    instance = args[0] if args else None

    if instance is not None:
        candidate = getattr(instance, "monitor", None)

        if isinstance(candidate, ApplicationMonitor):
            return candidate

    candidate = kwargs.get("monitor")

    if isinstance(candidate, ApplicationMonitor):
        return candidate

    return None


def _record_failure(
    monitor: ApplicationMonitor | None,
    span_id: str | None,
    error: Exception,
    duration_ms: float,
) -> None:
    """Record a failed execution without hiding the original exception."""
    if monitor is None or span_id is None:
        return

    try:
        monitor.record_pipeline_failure(
            span_id=span_id,
            error=f"{type(error).__name__}: {error}",
            execution_time_ms=duration_ms,
        )
    except Exception:
        # Observability failures must not replace application failures.
        return


def _record_success(
    monitor: ApplicationMonitor | None,
    span_id: str | None,
    duration_ms: float,
) -> None:
    """Record a successful execution."""
    if monitor is None or span_id is None:
        return

    monitor.record_pipeline_success(
        span_id=span_id,
        execution_time_ms=duration_ms,
    )


def observe(
    function: F | None = None,
    *,
    monitor: ApplicationMonitor | None = None,
    pipeline_name: str | None = None,
) -> F | Callable[[F], F]:
    """Track a synchronous function's execution.

    Usage:
        @observe
        def process_document(...):
            ...

        @observe(monitor=my_monitor, pipeline_name="ingestion")
        def process_document(...):
            ...
    """

    def decorator(func: F) -> F:
        name = pipeline_name or func.__qualname__

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                active_monitor = _resolve_monitor(
                    monitor,
                    args,
                    kwargs,
                )

                span_id = None
                execution_id = _build_execution_id(name)

                try:
                    if active_monitor is not None:
                        span = active_monitor.record_pipeline_start(
                            name,
                            execution_id,
                        )
                        span_id = span.span_id

                    started = perf_counter()

                    try:
                        result = await func(*args, **kwargs)
                    except Exception as exc:
                        duration_ms = (perf_counter() - started) * 1000
                        _record_failure(
                            active_monitor,
                            span_id,
                            exc,
                            duration_ms,
                        )
                        raise

                    duration_ms = (perf_counter() - started) * 1000
                    _record_success(
                        active_monitor,
                        span_id,
                        duration_ms,
                    )
                    return result

                except Exception:
                    raise

            return async_wrapper  # type: ignore[return-value]

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            active_monitor = _resolve_monitor(
                monitor,
                args,
                kwargs,
            )

            span_id = None
            execution_id = _build_execution_id(name)

            try:
                if active_monitor is not None:
                    span = active_monitor.record_pipeline_start(
                        name,
                        execution_id,
                    )
                    span_id = span.span_id

                started = perf_counter()

                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    duration_ms = (perf_counter() - started) * 1000
                    _record_failure(
                        active_monitor,
                        span_id,
                        exc,
                        duration_ms,
                    )
                    raise

                duration_ms = (perf_counter() - started) * 1000
                _record_success(
                    active_monitor,
                    span_id,
                    duration_ms,
                )

                return result

            except Exception:
                raise

        return wrapper  # type: ignore[return-value]

    if function is not None:
        return decorator(function)

    return decorator


def observe_method(
    *,
    monitor_attribute: str = "monitor",
    pipeline_name: str | None = None,
) -> Callable[[F], F]:
    """Decorate a method that stores an ApplicationMonitor on its instance."""

    if not isinstance(monitor_attribute, str) or not monitor_attribute.strip():
        raise ValueError("monitor_attribute must be a non-empty string.")

    def decorator(func: F) -> F:
        name = pipeline_name or func.__qualname__

        @wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            active_monitor = getattr(self, monitor_attribute, None)

            if not isinstance(active_monitor, ApplicationMonitor):
                return func(self, *args, **kwargs)

            execution_id = _build_execution_id(name)
            span = active_monitor.record_pipeline_start(name, execution_id)
            started = perf_counter()

            try:
                result = func(self, *args, **kwargs)
            except Exception as exc:
                duration_ms = (perf_counter() - started) * 1000
                _record_failure(
                    active_monitor,
                    span.span_id,
                    exc,
                    duration_ms,
                )
                raise

            duration_ms = (perf_counter() - started) * 1000
            _record_success(
                active_monitor,
                span.span_id,
                duration_ms,
            )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator
