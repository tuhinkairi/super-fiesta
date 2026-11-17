
from pathlib import Path
import sys

from context_aware_suggestion_rag.utils.platform_utils import (
    get_platform_info,
    is_windows,
    is_linux,
    is_macos,
    get_python_version,
    get_python_executable,
    get_cpu_count,
    get_home_directory,
    get_temp_directory,
    get_current_working_directory,
    get_environment_variable,
    get_system_environment,
    get_platform_name,
    get_runtime_info,
)


def test_platform_info():
    info = get_platform_info()

    assert isinstance(info, dict)
    assert "system" in info
    assert "python_version" in info


def test_platform_detection():
    assert isinstance(is_windows(), bool)
    assert isinstance(is_linux(), bool)
    assert isinstance(is_macos(), bool)

    assert sum([is_windows(), is_linux(), is_macos()]) <= 1


def test_python_version():
    version = get_python_version()

    assert isinstance(version, tuple)
    assert len(version) == 3
    assert version[:2] == sys.version_info[:2]


def test_python_executable():
    executable = get_python_executable()

    assert isinstance(executable, Path)
    assert executable.exists()


def test_cpu_count():
    assert get_cpu_count() >= 1


def test_system_directories():
    assert get_home_directory().exists()
    assert get_temp_directory().exists()
    assert get_current_working_directory().exists()


def test_environment_variable():
    import os

    os.environ["CASR_TEST_PLATFORM"] = "testing"

    assert get_environment_variable("CASR_TEST_PLATFORM") == "testing"
    assert get_environment_variable("CASR_MISSING", "fallback") == "fallback"


def test_system_environment():
    environment = get_system_environment()

    assert isinstance(environment, dict)
    assert all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in environment.items()
    )


def test_platform_name():
    assert get_platform_name() in {
        "windows",
        "linux",
        "macos",
        "unknown",
    }


def test_runtime_info():
    info = get_runtime_info()

    assert info["python_version"] == sys.version.split()[0]
    assert info["cpu_count"] >= 1
    assert isinstance(info["is_virtual_environment"], bool)


if __name__ == "__main__":
    tests = [
        test_platform_info,
        test_platform_detection,
        test_python_version,
        test_python_executable,
        test_cpu_count,
        test_system_directories,
        test_environment_variable,
        test_system_environment,
        test_platform_name,
        test_runtime_info,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All platform utility tests passed.")
