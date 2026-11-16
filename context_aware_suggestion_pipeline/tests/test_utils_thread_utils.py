
import threading
import time

from context_aware_suggestion_rag.utils.thread_utils import (
    ThreadSafeCounter,
    ThreadTaskResult,
    create_thread,
    get_current_thread_id,
    get_current_thread_name,
    get_thread_count,
    is_main_thread,
    join_thread,
    run_in_thread_pool,
    run_tasks_with_results,
    start_thread,
)


def test_thread_information():
    assert get_thread_count() >= 1
    assert get_current_thread_id() > 0
    assert get_current_thread_name()
    assert is_main_thread() is True


def test_create_thread():
    output = []

    thread = create_thread(
        target=lambda: output.append("completed"),
        name="test-thread",
    )

    assert isinstance(thread, threading.Thread)
    assert thread.name == "test-thread"
    assert not thread.is_alive()

    thread.start()
    assert join_thread(thread, timeout=2)
    assert output == ["completed"]


def test_start_thread():
    output = []

    thread = start_thread(
        target=lambda: output.append(10),
    )

    assert join_thread(thread, timeout=2)
    assert output == [10]


def test_thread_pool():
    def square(value):
        return value * value

    results = run_in_thread_pool(
        square,
        [
            ((2,), {}),
            ((3,), {}),
            ((4,), {}),
        ],
        max_workers=2,
    )

    assert results == [4, 9, 16]


def test_tasks_with_results():
    def successful_task():
        return "success"

    def failed_task():
        raise ValueError("expected failure")

    results = run_tasks_with_results(
        [
            successful_task,
            failed_task,
            lambda: 100,
        ],
        max_workers=2,
    )

    assert len(results) == 3
    assert results[0].success is True
    assert results[0].result == "success"
    assert results[1].success is False
    assert "ValueError" in results[1].error
    assert results[2].result == 100


def test_thread_safe_counter():
    counter = ThreadSafeCounter()

    threads = [
        start_thread(
            target=lambda: [
                counter.increment()
                for _ in range(1000)
            ]
        )
        for _ in range(5)
    ]

    for thread in threads:
        assert join_thread(thread, timeout=5)

    assert counter.get() == 5000

    counter.decrement(10)
    assert counter.get() == 4990

    counter.reset(0)
    assert counter.get() == 0


def test_thread_task_result():
    result = ThreadTaskResult(
        task_index=0,
        success=True,
        result="done",
    )

    assert result.success is True
    assert result.result == "done"


if __name__ == "__main__":
    tests = [
        test_thread_information,
        test_create_thread,
        test_start_thread,
        test_thread_pool,
        test_tasks_with_results,
        test_thread_safe_counter,
        test_thread_task_result,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All thread utility tests passed.")
