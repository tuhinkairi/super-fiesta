
import sys
import tempfile
from pathlib import Path
import subprocess

from context_aware_suggestion_rag.utils.process_utils import (
    ProcessResult,
    command_exists,
    get_process_output,
    run_command,
    run_python_script,
)


def test_process_result():
    result = ProcessResult(
        command=["python", "--version"],
        return_code=0,
        stdout="Python 3",
        stderr="",
        execution_time_seconds=0.1,
    )

    assert result.succeeded is True


def test_run_command():
    result = run_command(
        [sys.executable, "-c", "print('hello')"]
    )

    assert result.succeeded is True
    assert result.stdout.strip() == "hello"


def test_failed_command():
    result = run_command(
        [sys.executable, "-c", "raise SystemExit(2)"]
    )

    assert result.succeeded is False
    assert result.return_code == 2


def test_check_failure():
    try:
        run_command(
            [sys.executable, "-c", "raise SystemExit(3)"],
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        assert exc.returncode == 3
    else:
        raise AssertionError("Expected CalledProcessError.")


def test_command_exists():
    assert command_exists("python") is True


def test_get_process_output():
    output = get_process_output(
        [sys.executable, "-c", "print('output')"]
    )

    assert output.strip() == "output"


def test_run_python_script():
    with tempfile.TemporaryDirectory() as temp_dir:
        script = Path(temp_dir) / "sample.py"
        script.write_text(
            "print('script executed')",
            encoding="utf-8",
        )

        result = run_python_script(script)

        assert result.succeeded is True
        assert result.stdout.strip() == "script executed"


def test_timeout():
    result = run_command(
        [
            sys.executable,
            "-c",
            "import time; time.sleep(2)",
        ],
        timeout=0.1,
    )

    assert result.timed_out is True
    assert result.succeeded is False


if __name__ == "__main__":
    tests = [
        test_process_result,
        test_run_command,
        test_failed_command,
        test_check_failure,
        test_command_exists,
        test_get_process_output,
        test_run_python_script,
        test_timeout,
    ]

    for test in tests:
        test()
        print(f"{test.__name__}: PASS")

    print("All process utility tests passed.")
