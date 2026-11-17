"""System resource and process utilities."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any


def get_process_id() -> int:
    """Return the current process ID."""
    return os.getpid()


def get_parent_process_id() -> int:
    """Return the parent process ID."""
    return os.getppid()


def get_disk_usage(path: str | Path = ".") -> dict[str, int]:
    """Return total, used, and free disk space in bytes."""
    target = Path(path)

    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")

    usage = shutil.disk_usage(target)

    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
    }


def get_available_disk_space(path: str | Path = ".") -> int:
    """Return available disk space in bytes."""
    return get_disk_usage(path)["free"]


def get_total_disk_space(path: str | Path = ".") -> int:
    """Return total disk space in bytes."""
    return get_disk_usage(path)["total"]


def get_memory_usage() -> dict[str, int | None]:
    """Return process memory information where supported."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            from ctypes import wintypes

            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)

            kernel32.GetCurrentProcess.restype = wintypes.HANDLE
            kernel32.GetCurrentProcess.argtypes = []

            psapi.GetProcessMemoryInfo.argtypes = [
                wintypes.HANDLE,
                ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                wintypes.DWORD,
            ]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL

            counters = PROCESS_MEMORY_COUNTERS()
            counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)

            process_handle = kernel32.GetCurrentProcess()

            success = psapi.GetProcessMemoryInfo(
                process_handle,
                ctypes.byref(counters),
                counters.cb,
            )

            if not success:
                raise ctypes.WinError(ctypes.get_last_error())

            return {
                "rss": int(counters.WorkingSetSize),
                "peak_rss": int(counters.PeakWorkingSetSize),
                "virtual_memory": int(counters.PagefileUsage),
                "peak_virtual_memory": int(counters.PeakPagefileUsage),
            }

        except (ImportError, OSError, AttributeError, ctypes.ArgumentError):
            return {
                "rss": None,
                "peak_rss": None,
                "virtual_memory": None,
                "peak_virtual_memory": None,
            }

    if sys.platform.startswith("linux"):
        try:
            status_path = Path("/proc/self/status")
            values: dict[str, int | None] = {
                "rss": None,
                "peak_rss": None,
                "virtual_memory": None,
                "peak_virtual_memory": None,
            }

            mapping = {
                "VmRSS": "rss",
                "VmHWM": "peak_rss",
                "VmSize": "virtual_memory",
                "VmPeak": "peak_virtual_memory",
            }

            for line in status_path.read_text(encoding="utf-8").splitlines():
                key, separator, value = line.partition(":")

                if not separator or key not in mapping:
                    continue

                parts = value.strip().split()

                if parts:
                    values[mapping[key]] = int(parts[0]) * 1024

            return values

        except (OSError, ValueError):
            pass

    return {
        "rss": None,
        "peak_rss": None,
        "virtual_memory": None,
        "peak_virtual_memory": None,
    }


def get_environment_size() -> int:
    """Return the approximate size of environment variables in bytes."""
    return sum(
        len(key.encode("utf-8")) + len(value.encode("utf-8"))
        for key, value in os.environ.items()
    )


def get_open_file_limit() -> int | None:
    """Return the soft open-file limit on supported Unix systems."""
    try:
        import resource

        soft_limit, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
        return int(soft_limit)
    except (ImportError, OSError, ValueError):
        return None


def get_system_summary() -> dict[str, Any]:
    """Return a compact system resource summary."""
    return {
        "process_id": get_process_id(),
        "parent_process_id": get_parent_process_id(),
        "cpu_count": os.cpu_count() or 1,
        "memory": get_memory_usage(),
        "disk": get_disk_usage(Path.cwd()),
        "environment_size_bytes": get_environment_size(),
        "open_file_limit": get_open_file_limit(),
    }


__all__ = [
    "get_process_id",
    "get_parent_process_id",
    "get_disk_usage",
    "get_available_disk_space",
    "get_total_disk_space",
    "get_memory_usage",
    "get_environment_size",
    "get_open_file_limit",
    "get_system_summary",
]
