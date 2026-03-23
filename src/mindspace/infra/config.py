"""Application configuration via environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MINDSPACE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Reads OPENAI_API_KEY (no prefix) since it's a standard env var
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    data_dir: str = "./data"

    # Chunking
    chunk_max_tokens: int = 500
    chunk_overlap_tokens: int = 50

    # Hybrid search
    hybrid_search_enabled: bool = True

    # Web server
    server_host: str = "127.0.0.1"
    server_port: int = 8000

    # Claude API
    anthropic_api_key: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")
    claude_model: str = "claude-sonnet-4-20250514"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the singleton settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset settings (for testing)."""
    global _settings
    _settings = None
