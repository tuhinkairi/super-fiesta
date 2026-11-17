
from context_aware_suggestion_rag.security.rate_limiter import (
    RateLimitConfig,
    SlidingWindowRateLimiter,
)


def test_default_configuration():
    config = RateLimitConfig()

    assert config.max_requests == 60
    assert config.window_seconds == 60.0

    print("Default rate-limit configuration: PASS")


def test_custom_configuration():
    config = RateLimitConfig(
        max_requests=3,
        window_seconds=10,
    )

    assert config.max_requests == 3
    assert config.window_seconds == 10.0

    print("Custom rate-limit configuration: PASS")


def test_request_limit():
    limiter = SlidingWindowRateLimiter(
        RateLimitConfig(max_requests=2, window_seconds=60)
    )

    first = limiter.allow_request("user_1")
    second = limiter.allow_request("user_1")
    third = limiter.allow_request("user_1")

    assert first.allowed is True
    assert second.allowed is True
    assert second.remaining_requests == 0
    assert third.allowed is False
    assert third.retry_after_seconds > 0

    print("Request limit enforcement: PASS")


def test_client_isolation():
    limiter = SlidingWindowRateLimiter(
        RateLimitConfig(max_requests=1)
    )

    assert limiter.allow_request("user_1").allowed
    assert limiter.allow_request("user_2").allowed
    assert not limiter.allow_request("user_1").allowed

    print("Client isolation: PASS")


def test_check_does_not_consume_request():
    limiter = SlidingWindowRateLimiter(
        RateLimitConfig(max_requests=1)
    )

    decision = limiter.check("user_1")

    assert decision.allowed is True
    assert limiter.get_request_count("user_1") == 0

    assert limiter.allow_request("user_1").allowed

    print("Non-consuming rate-limit check: PASS")


def test_reset():
    limiter = SlidingWindowRateLimiter(
        RateLimitConfig(max_requests=1)
    )

    limiter.allow_request("user_1")

    assert limiter.reset("user_1") is True
    assert limiter.reset("user_1") is False
    assert limiter.allow_request("user_1").allowed

    print("Individual client reset: PASS")


def test_reset_all():
    limiter = SlidingWindowRateLimiter()

    limiter.allow_request("user_1")
    limiter.allow_request("user_2")

    assert limiter.reset_all() == 2
    assert limiter.get_client_count() == 0

    print("Global rate-limit reset: PASS")


def test_invalid_configuration():
    try:
        RateLimitConfig(max_requests=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid request limit to fail.")

    try:
        RateLimitConfig(window_seconds=0)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid window to fail.")

    print("Invalid configuration validation: PASS")


def test_health_and_close():
    limiter = SlidingWindowRateLimiter()

    assert limiter.health_check() is True

    limiter.close()

    assert limiter.health_check() is False

    try:
        limiter.allow_request("user_1")
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected closed limiter to reject requests.")

    print("Rate limiter health and shutdown: PASS")


if __name__ == "__main__":
    test_default_configuration()
    test_custom_configuration()
    test_request_limit()
    test_client_isolation()
    test_check_does_not_consume_request()
    test_reset()
    test_reset_all()
    test_invalid_configuration()
    test_health_and_close()

    print("\nAll security rate-limiter tests passed.")
