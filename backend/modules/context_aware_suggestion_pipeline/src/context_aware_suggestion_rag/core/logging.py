"""
Centralized logging configuration.

Provides consistent logging utilities for all modules in the
Context-Aware Suggestion RAG package.
"""

import logging
import logging.config
from pathlib import Path
from typing import Final

from backend.modules.context_aware_suggestion_pipeline.src.context_aware_suggestion_rag.config.settings import get_settings


DEFAULT_LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DEFAULT_DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"

PACKAGE_LOGGER_NAME: Final[str] = "context_aware_suggestion_rag"


def configure_logging(
    level: str | None = None,
    log_file: str | Path | None = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
) -> None:
    """
    Configure package-wide logging.

    Args:
        level: Logging level. Defaults to the application setting.
        log_file: Optional path to a file where logs should be written.
        log_format: Format used for log messages.
        date_format: Format used for timestamps.
    """

    settings = get_settings()

    selected_level = (level or settings.log_level).upper()

    if selected_level not in logging._nameToLevel:
        raise ValueError(
            f"Invalid logging level: {selected_level}"
        )

    formatter = logging.Formatter(
        fmt=log_format,
        datefmt=date_format,
    )

    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    logger.setLevel(selected_level)
    logger.propagate = False

    # Remove existing handlers to prevent duplicate log messages.
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()

    # Console handler.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(selected_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler.
    if log_file is not None:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            file_path,
            encoding="utf-8",
        )
        file_handler.setLevel(selected_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a logger belonging to this package.

    Args:
        name: Module name, usually __name__.

    Returns:
        A configured package logger.
    """

    if name is None:
        return logging.getLogger(PACKAGE_LOGGER_NAME)

    if name == PACKAGE_LOGGER_NAME or name.startswith(
        f"{PACKAGE_LOGGER_NAME}."
    ):
        return logging.getLogger(name)

    return logging.getLogger(f"{PACKAGE_LOGGER_NAME}.{name}")


__all__ = [
    "configure_logging",
    "get_logger",
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_DATE_FORMAT",
    "PACKAGE_LOGGER_NAME",
]
