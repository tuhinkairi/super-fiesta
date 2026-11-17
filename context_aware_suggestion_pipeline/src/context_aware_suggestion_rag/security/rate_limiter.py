"""
Thread-safe sliding-window rate limiter.

Provides per-client request limits using monotonic time.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from threading import RLock
from time import monotonic


@dataclass(frozen=True, slots=True)
class RateLimitConfig:
    """Configuration for request rate limiting."""

    max_requests: int = 60
    window_seconds: float = 60.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_requests, bool)
            or not isinstance(self.max_requests, int)
            or self.max_requests <= 0
        ):
            raise ValueError("max_requests must be a positive integer.")

        if (
            isinstance(self.window_seconds, bool)
            or not isinstance(self.window_seconds, (int, float))
            or self.window_seconds <= 0
        ):
            raise ValueError("window_seconds must be positive.")

        object.__setattr__(
            self,
            "window_seconds",
            float(self.window_seconds),
        )


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    """Result of a rate-limit check."""

    allowed: bool
    client_id: str
    remaining_requests: int
    limit: int
    retry_after_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not isinstance(self.allowed, bool):
            raise TypeError("allowed must be a boolean.")

        if not isinstance(self.client_id, str) or not self.client_id.strip():
            raise ValueError("client_id must be a non-empty string.")

        if self.remaining_requests < 0:
            raise ValueError("remaining_requests cannot be negative.")

        if self.limit <= 0:
            raise ValueError("limit must be positive.")

        if self.retry_after_seconds < 0:
            raise ValueError("retry_after_seconds cannot be negative.")


class SlidingWindowRateLimiter:
    """Applies per-client sliding-window request limits."""

    def __init__(
        self,
        config: RateLimitConfig | None = None,
    ) -> None:
        self.config = config or RateLimitConfig()
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = RLock()
        self._closed = False

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Rate limiter is closed.")

    @staticmethod
    def _validate_client_id(client_id: str) -> str:
        if not isinstance(client_id, str):
            raise TypeError("client_id must be a string.")

        client_id = client_id.strip()

        if not client_id:
            raise ValueError("client_id cannot be empty.")

        return client_id

    def _remove_expired(
        self,
        timestamps: deque[float],
        current_time: float,
    ) -> None:
        cutoff = current_time - self.config.window_seconds

        while timestamps and timestamps[0] <= cutoff:
            timestamps.popleft()

    def check(self, client_id: str) -> RateLimitDecision:
        """Check whether a client can make another request."""
        self._ensure_open()
        client_id = self._validate_client_id(client_id)

        current_time = monotonic()

        with self._lock:
            timestamps = self._requests[client_id]
            self._remove_expired(timestamps, current_time)

            remaining = max(
                0,
                self.config.max_requests - len(timestamps),
            )

            retry_after = 0.0

            if len(timestamps) >= self.config.max_requests:
                retry_after = max(
                    0.0,
                    timestamps[0]
                    + self.config.window_seconds
                    - current_time,
                )

            return RateLimitDecision(
                allowed=remaining > 0,
                client_id=client_id,
                remaining_requests=remaining,
                limit=self.config.max_requests,
                retry_after_seconds=retry_after,
            )

    def allow_request(self, client_id: str) -> RateLimitDecision:
        """
        Atomically check and record a request.

        A request is recorded only when it is allowed.
        """
        self._ensure_open()
        client_id = self._validate_client_id(client_id)

        current_time = monotonic()

        with self._lock:
            timestamps = self._requests[client_id]
            self._remove_expired(timestamps, current_time)

            if len(timestamps) >= self.config.max_requests:
                retry_after = max(
                    0.0,
                    timestamps[0]
                    + self.config.window_seconds
                    - current_time,
                )

                return RateLimitDecision(
                    allowed=False,
                    client_id=client_id,
                    remaining_requests=0,
                    limit=self.config.max_requests,
                    retry_after_seconds=retry_after,
                )

            timestamps.append(current_time)

            return RateLimitDecision(
                allowed=True,
                client_id=client_id,
                remaining_requests=(
                    self.config.max_requests - len(timestamps)
                ),
                limit=self.config.max_requests,
            )

    def reset(self, client_id: str) -> bool:
        """Remove the rate-limit history of a client."""
        self._ensure_open()
        client_id = self._validate_client_id(client_id)

        with self._lock:
            return self._requests.pop(client_id, None) is not None

    def reset_all(self) -> int:
        """Clear all client histories and return the number removed."""
        self._ensure_open()

        with self._lock:
            count = len(self._requests)
            self._requests.clear()
            return count

    def get_request_count(self, client_id: str) -> int:
        """Return the active request count for a client."""
        self._ensure_open()
        client_id = self._validate_client_id(client_id)

        current_time = monotonic()

        with self._lock:
            timestamps = self._requests.get(client_id)

            if timestamps is None:
                return 0

            self._remove_expired(timestamps, current_time)

            if not timestamps:
                self._requests.pop(client_id, None)
                return 0

            return len(timestamps)

    def get_client_count(self) -> int:
        """Return the number of clients with active request history."""
        self._ensure_open()

        current_time = monotonic()

        with self._lock:
            expired_clients = []

            for client_id, timestamps in self._requests.items():
                self._remove_expired(timestamps, current_time)

                if not timestamps:
                    expired_clients.append(client_id)

            for client_id in expired_clients:
                self._requests.pop(client_id, None)

            return len(self._requests)

    def health_check(self) -> bool:
        """Check whether the limiter is operational."""
        return not self._closed

    def close(self) -> None:
        """Clear stored histories and close the limiter."""
        with self._lock:
            self._requests.clear()
            self._closed = True

    def __enter__(self) -> SlidingWindowRateLimiter:
        self._ensure_open()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.close()
