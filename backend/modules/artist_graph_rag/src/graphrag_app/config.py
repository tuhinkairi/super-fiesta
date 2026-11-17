
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


# Load the project's .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[5]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


class Settings(BaseModel):
    """Application configuration for Neo4j AuraDB and Gemini."""

    # Neo4j AuraDB configuration
    neo4j_uri: str = Field(min_length=1)
    neo4j_username: str = Field(min_length=1)
    neo4j_password: str = Field(min_length=1)
    neo4j_database: str = Field(default="neo4j", min_length=1)

    # LLM configuration
    llm_provider: str = "gemini"
    llm_api_key: str = Field(min_length=1)
    llm_model: str = Field(min_length=1)

    @field_validator(
        "neo4j_uri",
        "neo4j_username",
        "neo4j_password",
        "neo4j_database",
        "llm_provider",
        "llm_api_key",
        "llm_model",
    )
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        """Remove surrounding whitespace and reject empty values."""

        value = value.strip()

        if not value:
            raise ValueError("Configuration value cannot be empty.")

        return value

    @field_validator("neo4j_uri")
    @classmethod
    def validate_neo4j_uri(cls, value: str) -> str:
        """Validate the Neo4j AuraDB connection URI."""

        if not value.startswith("neo4j+s://"):
            raise ValueError(
                "Invalid Neo4j AuraDB URI. "
                "Expected format: "
                "neo4j+s://<instance-id>.databases.neo4j.io"
            )

        return value.rstrip("/")

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        """Validate the configured LLM provider."""

        value = value.lower()

        if value != "gemini":
            raise ValueError(
                "Unsupported LLM provider. Currently supported: gemini."
            )

        return value


def load_settings() -> Settings:
    """Load and validate application settings."""

    return Settings(
        neo4j_uri=os.getenv("NEO4J_URI", ""),
        neo4j_username=os.getenv("NEO4J_USERNAME", ""),
        neo4j_password=os.getenv("NEO4J_PASSWORD", ""),
        neo4j_database=os.getenv("NEO4J_DATABASE", "neo4j"),
        llm_provider=os.getenv("LLM_PROVIDER", "gemini"),
        llm_api_key=os.getenv("GEMINI_API_KEY", os.getenv("LLM_API_KEY", "")),
        llm_model=os.getenv(
            "ARTIST_GRAPH_MODEL", os.getenv("GEMINI_MODEL", os.getenv("LLM_MODEL", ""))
        ),
    )


# Shared application settings
settings = load_settings()
