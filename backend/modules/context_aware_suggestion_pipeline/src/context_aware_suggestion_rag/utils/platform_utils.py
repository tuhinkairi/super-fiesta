"""Cross-platform system and runtime utilities."""

from __future__ import annotations

import os
import platform
import sys
from pathlib import Path
from typing import Any


def get_platform_info() -> dict[str, str]:
    """Return basic operating-system and runtime information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }


def is_windows() -> bool:
    """Return True when running on Windows."""
    return sys.platform.startswith("win")


def is_linux() -> bool:
    """Return True when running on Linux."""
    return sys.platform.startswith("linux")


def is_macos() -> bool:
    """Return True when running on macOS."""
    return sys.platform == "darwin"


def get_python_version() -> tuple[int, int, int]:
    """Return the current Python version as a tuple."""
    version = sys.version_info
    return version.major, version.minor, version.micro


def get_python_executable() -> Path:
    """Return the path to the current Python executable."""
    return Path(sys.executable).resolve()


def get_cpu_count() -> int:
    """Return the number of available CPUs, with a safe fallback."""
    return os.cpu_count() or 1


def get_home_directory() -> Path:
    """Return the current user's home directory."""
    return Path.home()


def get_temp_directory() -> Path:
    """Return the system temporary directory."""
    import tempfile

    return Path(tempfile.gettempdir())


def get_current_working_directory() -> Path:
    """Return the current working directory."""
    return Path.cwd()


def get_environment_variable(
    name: str,
    default: str | None = None,
) -> str | None:
    """Read an environment variable without modifying the environment."""
    if not isinstance(name, str):
        raise TypeError("name must be a string.")

    if not name.strip():
        raise ValueError("name cannot be empty.")

    if default is not None and not isinstance(default, str):
        raise TypeError("default must be a string or None.")

    return os.environ.get(name, default)


def get_system_environment() -> dict[str, str]:
    """Return a copy of the current process environment."""
    return dict(os.environ)


def get_platform_name() -> str:
    """Return a normalized platform name."""
    if is_windows():
        return "windows"

    if is_linux():
        return "linux"

    if is_macos():
        return "macos"

    return platform.system().lower() or "unknown"


def get_runtime_info() -> dict[str, Any]:
    """Return useful Python runtime information."""
    return {
        "python_version": platform.python_version(),
        "python_executable": str(get_python_executable()),
        "python_implementation": platform.python_implementation(),
        "platform": get_platform_name(),
        "cpu_count": get_cpu_count(),
        "prefix": sys.prefix,
        "base_prefix": sys.base_prefix,
        "is_virtual_environment": sys.prefix != sys.base_prefix,
    }


__all__ = [
    "get_platform_info",
    "is_windows",
    "is_linux",
    "is_macos",
    "get_python_version",
    "get_python_executable",
    "get_cpu_count",
    "get_home_directory",
    "get_temp_directory",
    "get_current_working_directory",
    "get_environment_variable",
    "get_system_environment",
    "get_platform_name",
    "get_runtime_info",
]
