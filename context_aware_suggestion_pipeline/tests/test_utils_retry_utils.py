
from context_aware_suggestion_rag.utils.retry_utils import (
    exponential_backoff,
    retry,
    retry_call,
    retrying_iterator,
)


def test_exponential_backoff():
    assert exponential_backoff(1) == 1.0
    assert exponential_backoff(2) == 2.0
    assert exponential_backoff(3) == 4.0
    assert exponential_backoff(10, maximum=5) == 5.0


def test_retry_call_success():
    result = retry_call(
        lambda value: value * 2,
        5,
        max_attempts=3,
    )

    assert result == 10


def test_retry_call_after_failure():
    attempts = {"count": 0}

    def unstable_function():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise RuntimeError("Temporary failure")

        return "success"

    result = retry_call(
        unstable_function,
        max_attempts=3,
        wait_max=0,
    )

    assert result == "success"
    assert attempts["count"] == 3


def test_retry_decorator():
    attempts = {"count": 0}

    @retry(max_attempts=3, wait_max=0)
    def unstable_function():
        attempts["count"] += 1

        if attempts["count"] < 2:
            raise ValueError("Temporary error")

        return "completed"

    assert unstable_function() == "completed"
    assert attempts["count"] == 2


def test_retry_exception_filter():
    attempts = {"count": 0}

    def failing_function():
        attempts["count"] += 1
        raise ValueError("Permanent error")

    try:
        retry_call(
            failing_function,
            max_attempts=3,
            exceptions=(RuntimeError,),
            wait_max=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError.")

    assert attempts["count"] == 1


def test_retrying_iterator():
    retryer = retrying_iterator(
        max_attempts=2,
        wait_max=0,
    )

    assert retryer is not None


if __name__ == "__main__":
    tests = [
        test_exponential_backoff,
        test_retry_call_success,
        test_retry_call_after_failure,
        test_retry_decorator,
        test_retry_exception_filter,
        test_retrying_iterator,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All retry utility tests passed.")
