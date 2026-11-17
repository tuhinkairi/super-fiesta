"""Utilities for executing and managing external processes."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Any


@dataclass(slots=True)
class ProcessResult:
    """Result returned by an external process."""

    command: list[str]
    return_code: int
    stdout: str
    stderr: str
    execution_time_seconds: float
    timed_out: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.command, list):
            raise TypeError("command must be a list.")

        if any(not isinstance(item, str) for item in self.command):
            raise TypeError("Every command argument must be a string.")

        if isinstance(self.return_code, bool) or not isinstance(
            self.return_code, int
        ):
            raise TypeError("return_code must be an integer.")

        if not isinstance(self.stdout, str):
            raise TypeError("stdout must be a string.")

        if not isinstance(self.stderr, str):
            raise TypeError("stderr must be a string.")

        if isinstance(self.execution_time_seconds, bool) or not isinstance(
            self.execution_time_seconds, (int, float)
        ):
            raise TypeError("execution_time_seconds must be numeric.")

        if self.execution_time_seconds < 0:
            raise ValueError("execution_time_seconds cannot be negative.")

        if not isinstance(self.timed_out, bool):
            raise TypeError("timed_out must be a boolean.")

    @property
    def succeeded(self) -> bool:
        """Return whether the process completed successfully."""
        return self.return_code == 0 and not self.timed_out


def _validate_command(command: Sequence[str | Path]) -> list[str]:
    """Validate and normalize a command argument sequence."""
    if not isinstance(command, Sequence):
        raise TypeError("command must be a sequence.")

    if isinstance(command, (str, bytes, bytearray)):
        raise TypeError("command must be a sequence of arguments.")

    if not command:
        raise ValueError("command cannot be empty.")

    normalized: list[str] = []

    for argument in command:
        if not isinstance(argument, (str, Path)):
            raise TypeError("Command arguments must be strings or Path objects.")

        value = str(argument)

        if not value:
            raise ValueError("Command arguments cannot be empty.")

        normalized.append(value)

    return normalized


def run_command(
    command: Sequence[str | Path],
    *,
    cwd: str | Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = 60.0,
    check: bool = False,
    encoding: str = "utf-8",
) -> ProcessResult:
    """Run an external command without invoking a shell."""
    normalized_command = _validate_command(command)

    if cwd is not None:
        cwd = Path(cwd)

        if not cwd.exists():
            raise FileNotFoundError(f"Working directory does not exist: {cwd}")

        if not cwd.is_dir():
            raise NotADirectoryError(f"Working directory is not a directory: {cwd}")

    if env is not None:
        if not isinstance(env, Mapping):
            raise TypeError("env must be a mapping.")

        if any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in env.items()
        ):
            raise TypeError("Environment keys and values must be strings.")

    if timeout is not None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric or None.")

        if timeout <= 0:
            raise ValueError("timeout must be greater than zero.")

    if not isinstance(check, bool):
        raise TypeError("check must be a boolean.")

    if not isinstance(encoding, str) or not encoding:
        raise ValueError("encoding must be a non-empty string.")

    import time

    start_time = time.perf_counter()

    try:
        completed = subprocess.run(
            normalized_command,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            timeout=timeout,
            check=False,
            capture_output=True,
            text=True,
            encoding=encoding,
            errors="replace",
            shell=False,
        )

        elapsed = time.perf_counter() - start_time

        result = ProcessResult(
            command=normalized_command,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            execution_time_seconds=elapsed,
        )

    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start_time

        stdout = exc.stdout or ""
        stderr = exc.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(encoding, errors="replace")

        if isinstance(stderr, bytes):
            stderr = stderr.decode(encoding, errors="replace")

        result = ProcessResult(
            command=normalized_command,
            return_code=-1,
            stdout=stdout,
            stderr=stderr,
            execution_time_seconds=elapsed,
            timed_out=True,
        )

    if check and not result.succeeded:
        if result.timed_out:
            raise subprocess.TimeoutExpired(
                normalized_command,
                timeout,
                output=result.stdout,
                stderr=result.stderr,
            )

        raise subprocess.CalledProcessError(
            result.return_code,
            normalized_command,
            output=result.stdout,
            stderr=result.stderr,
        )

    return result


def run_python_script(
    script_path: str | Path,
    arguments: Sequence[str] | None = None,
    *,
    cwd: str | Path | None = None,
    timeout: float | None = 60.0,
    check: bool = False,
) -> ProcessResult:
    """Execute a Python script using the current Python interpreter."""
    script = Path(script_path)

    if not script.exists():
        raise FileNotFoundError(f"Python script not found: {script}")

    if not script.is_file():
        raise ValueError(f"Python script path is not a file: {script}")

    if arguments is None:
        arguments = []

    if not isinstance(arguments, Sequence):
        raise TypeError("arguments must be a sequence of strings.")

    if isinstance(arguments, (str, bytes, bytearray)):
        raise TypeError("arguments must be a sequence, not a single string.")

    if any(not isinstance(argument, str) for argument in arguments):
        raise TypeError("Every script argument must be a string.")

    command = [sys.executable, str(script), *arguments]

    return run_command(
        command,
        cwd=cwd,
        timeout=timeout,
        check=check,
    )


def command_exists(command: str) -> bool:
    """Check whether an executable is available on PATH."""
    if not isinstance(command, str):
        raise TypeError("command must be a string.")

    if not command.strip():
        raise ValueError("command cannot be empty.")

    return shutil.which(command) is not None


def get_process_output(
    command: Sequence[str | Path],
    *,
    cwd: str | Path | None = None,
    timeout: float | None = 60.0,
) -> str:
    """Run a command and return its standard output."""
    result = run_command(
        command,
        cwd=cwd,
        timeout=timeout,
        check=True,
    )

    return result.stdout


__all__ = [
    "ProcessResult",
    "run_command",
    "run_python_script",
    "command_exists",
    "get_process_output",
]
