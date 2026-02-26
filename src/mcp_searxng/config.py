"""Configuration management for MCP SearXNG server."""

from typing import Literal

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # SearXNG Configuration
    searxng_url: HttpUrl = Field(
        default=HttpUrl("https://searxng.pixelcrazed.com"),
        description="SearXNG instance URL",
    )
    searxng_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )
    searxng_max_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum results per query",
    )

    # MCP Server Configuration
    mcp_transport: Literal["stdio", "sse"] = Field(
        default="stdio",
        description="MCP transport type",
    )
    mcp_port: int = Field(
        default=3000,
        ge=1,
        le=65535,
        description="Server port for SSE transport",
    )

    # Logging
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Logging level",
    )

    # Caching (for future phases)
    cache_enabled: bool = Field(
        default=False,
        description="Enable result caching",
    )

    @property
    def searxng_url_str(self) -> str:
        """Get SearXNG URL as string."""
        return str(self.searxng_url).rstrip("/")


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
