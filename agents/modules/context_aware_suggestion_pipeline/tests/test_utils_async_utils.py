
import asyncio

from context_aware_suggestion_rag.utils.async_utils import (
    async_retry,
    cancel_tasks,
    gather_with_concurrency,
    retry_async_call,
    run_tasks,
    run_with_timeout,
    wait_for_tasks,
)


async def sample_value(value):
    return value


async def test_run_with_timeout():
    result = await run_with_timeout(sample_value("success"), 2)
    assert result == "success"


async def test_timeout_default():
    async def slow_task():
        await asyncio.sleep(0.2)
        return "completed"

    result = await run_with_timeout(
        slow_task(),
        0.01,
        default="timeout",
        raise_on_timeout=False,
    )

    assert result == "timeout"


async def test_retry_async_call():
    attempts = {"count": 0}

    async def unstable_task():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise RuntimeError("Temporary failure")

        return "success"

    result = await retry_async_call(
        unstable_task,
        max_attempts=3,
        wait_max=0,
    )

    assert result == "success"
    assert attempts["count"] == 3


async def test_async_retry_decorator():
    attempts = {"count": 0}

    @async_retry(max_attempts=3, wait_max=0)
    async def unstable_task():
        attempts["count"] += 1

        if attempts["count"] < 2:
            raise ValueError("Temporary error")

        return "completed"

    result = await unstable_task()

    assert result == "completed"
    assert attempts["count"] == 2


async def test_gather_with_concurrency():
    active = {"count": 0, "maximum": 0}

    async def task(value):
        active["count"] += 1
        active["maximum"] = max(
            active["maximum"],
            active["count"],
        )

        await asyncio.sleep(0.02)

        active["count"] -= 1
        return value

    results = await gather_with_concurrency(
        [task(i) for i in range(6)],
        limit=2,
    )

    assert results == [0, 1, 2, 3, 4, 5]
    assert active["maximum"] <= 2


async def test_run_tasks():
    results = await run_tasks(
        [
            lambda: sample_value(1),
            lambda: sample_value(2),
            lambda: sample_value(3),
        ],
        limit=2,
    )

    assert results == [1, 2, 3]


async def test_cancel_tasks():
    async def long_task():
        await asyncio.sleep(10)

    tasks = [
        asyncio.create_task(long_task()),
        asyncio.create_task(long_task()),
    ]

    await asyncio.sleep(0)

    cancelled = await cancel_tasks(tasks)

    assert cancelled == 2
    assert all(task.cancelled() for task in tasks)


async def test_wait_for_tasks():
    async def quick_task():
        await asyncio.sleep(0.01)
        return "done"

    tasks = [
        asyncio.create_task(quick_task()),
        asyncio.create_task(quick_task()),
    ]

    done, pending = await wait_for_tasks(tasks, timeout=2)

    assert len(done) == 2
    assert len(pending) == 0


if __name__ == "__main__":
    tests = [
        test_run_with_timeout,
        test_timeout_default,
        test_retry_async_call,
        test_async_retry_decorator,
        test_gather_with_concurrency,
        test_run_tasks,
        test_cancel_tasks,
        test_wait_for_tasks,
    ]

    for test in tests:
        asyncio.run(test())
        print(f"{test.__name__}: PASS")

    print("All async utility tests passed.")
