
from pathlib import Path

from context_aware_suggestion_rag.utils.system_utils import (
    get_process_id,
    get_parent_process_id,
    get_disk_usage,
    get_available_disk_space,
    get_total_disk_space,
    get_memory_usage,
    get_environment_size,
    get_open_file_limit,
    get_system_summary,
)


def test_process_ids():
    assert get_process_id() > 0
    assert get_parent_process_id() >= 0


def test_disk_usage():
    usage = get_disk_usage(Path.cwd())

    assert usage["total"] > 0
    assert usage["used"] >= 0
    assert usage["free"] >= 0
    assert usage["total"] == usage["used"] + usage["free"]


def test_disk_space_helpers():
    assert get_available_disk_space() >= 0
    assert get_total_disk_space() > 0


def test_memory_usage():
    memory = get_memory_usage()

    assert isinstance(memory, dict)

    for value in memory.values():
        assert value is None or value >= 0


def test_environment_size():
    assert get_environment_size() >= 0


def test_open_file_limit():
    result = get_open_file_limit()

    assert result is None or result > 0


def test_system_summary():
    summary = get_system_summary()

    assert summary["process_id"] > 0
    assert summary["cpu_count"] >= 1
    assert "memory" in summary
    assert "disk" in summary


if __name__ == "__main__":
    tests = [
        test_process_ids,
        test_disk_usage,
        test_disk_space_helpers,
        test_memory_usage,
        test_environment_size,
        test_open_file_limit,
        test_system_summary,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All system utility tests passed.")
