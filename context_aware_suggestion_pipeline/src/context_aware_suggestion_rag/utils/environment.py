"""Environment variable utilities."""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def get_env(
    name: str,
    default: str | None = None,
    *,
    strip: bool = True,
) -> str | None:
    """Read an environment variable."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Environment variable name cannot be empty")

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip() if strip else value


def get_env_bool(
    name: str,
    default: bool = False,
) -> bool:
    """Read an environment variable as a boolean."""
    if not isinstance(default, bool):
        raise TypeError("default must be a boolean")

    value = get_env(name)

    if value is None:
        return default

    normalized = value.casefold()

    if normalized in {"true", "1", "yes", "y", "on"}:
        return True

    if normalized in {"false", "0", "no", "n", "off"}:
        return False

    raise ValueError(f"Invalid boolean environment value for {name}")


def get_env_int(
    name: str,
    default: int | None = None,
) -> int | None:
    """Read an environment variable as an integer."""
    value = get_env(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as error:
        raise ValueError(
            f"Environment variable {name} must be an integer"
        ) from error


def get_env_float(
    name: str,
    default: float | None = None,
) -> float | None:
    """Read an environment variable as a float."""
    value = get_env(name)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError as error:
        raise ValueError(
            f"Environment variable {name} must be a float"
        ) from error


def get_required_env(name: str) -> str:
    """Read a required, non-empty environment variable."""
    value = get_env(name)

    if value is None or not value:
        raise ValueError(
            f"Required environment variable is missing: {name}"
        )

    return value


def get_env_list(
    name: str,
    default: list[str] | None = None,
    *,
    separator: str = ",",
) -> list[str]:
    """Read a comma-separated environment variable."""
    if not isinstance(separator, str) or not separator:
        raise ValueError("separator must be a non-empty string")

    value = get_env(name)

    if value is None:
        return list(default) if default is not None else []

    return [
        item.strip()
        for item in value.split(separator)
        if item.strip()
    ]


def get_env_mapping(
    prefix: str,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Collect environment variables sharing a prefix."""
    if not isinstance(prefix, str):
        raise TypeError("prefix must be a string")

    source = os.environ if environ is None else environ

    return {
        key[len(prefix):]: value
        for key, value in source.items()
        if key.startswith(prefix)
    }


def set_env_defaults(
    defaults: Mapping[str, Any],
    *,
    overwrite: bool = False,
) -> None:
    """Set environment variables from defaults."""
    if not isinstance(defaults, Mapping):
        raise TypeError("defaults must be a mapping")

    for name, value in defaults.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Environment variable names must be non-empty")

        if not overwrite and name in os.environ:
            continue

        if value is None:
            continue

        os.environ[name] = str(value)


def load_env_file(
    path: str | Path,
    *,
    overwrite: bool = False,
) -> int:
    """Load simple KEY=VALUE entries from an environment file.

    Existing environment variables are preserved unless overwrite=True.
    This is a deliberately small parser; use pydantic-settings for the
    project's full .env configuration.
    """
    env_path = Path(path)

    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")

    if not env_path.is_file():
        raise ValueError(f"Environment path is not a file: {env_path}")

    loaded = 0

    for line_number, raw_line in enumerate(
        env_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[7:].strip()

        if "=" not in line:
            raise ValueError(
                f"Invalid environment entry at line {line_number}"
            )

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip()

        if not name:
            raise ValueError(
                f"Missing environment variable name at line {line_number}"
            )

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {"'", '"'}
        ):
            value = value[1:-1]

        if overwrite or name not in os.environ:
            os.environ[name] = value
            loaded += 1

    return loaded
