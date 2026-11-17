
from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from model_config import AGENTS_ROOT


# Project root: large project/
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class InspirationSettings(BaseSettings):
    """
    Configuration for the Inspiration Ingestion module.
    """

    # Where uploaded files and processed data will be stored.
    storage_dir: Path = PROJECT_ROOT / "storage"

    # Maximum allowed upload size.
    max_file_size_mb: int = Field(default=20, gt=0)

    # Text chunking configuration.
    chunk_size: int = Field(default=1000, gt=0)
    chunk_overlap: int = Field(default=150, ge=0)

    model_config = SettingsConfigDict(
        env_file=AGENTS_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_chunk_settings(self):
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )
        return self


@lru_cache
def get_inspiration_settings() -> InspirationSettings:
    """
    Return cached application settings.
    """
    return InspirationSettings()
