"""Tests for MCP SearXNG configuration module."""

import os
from unittest.mock import patch

import pytest
from pydantic import HttpUrl

from mcp_searxng.config import Settings, get_settings


class TestSettings:
    """Test cases for Settings class."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.searxng_url == HttpUrl("https://searxng.pixelcrazed.com")
        assert settings.searxng_timeout == 30
        assert settings.searxng_max_results == 10
        assert settings.mcp_transport == "stdio"
        assert settings.mcp_port == 3000
        assert settings.log_level == "info"
        assert settings.cache_enabled is False

    def test_custom_settings_from_env(self):
        """Test loading settings from environment variables."""
        env_vars = {
            "SEARXNG_URL": "https://custom.searxng.com",
            "SEARXNG_TIMEOUT": "60",
            "SEARXNG_MAX_RESULTS": "20",
            "MCP_TRANSPORT": "sse",
            "MCP_PORT": "8080",
            "LOG_LEVEL": "debug",
            "CACHE_ENABLED": "true",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            assert str(settings.searxng_url) == "https://custom.searxng.com/"
            assert settings.searxng_timeout == 60
            assert settings.searxng_max_results == 20
            assert settings.mcp_transport == "sse"
            assert settings.mcp_port == 8080
            assert settings.log_level == "debug"
            assert settings.cache_enabled is True

    def test_searxng_url_str_property(self):
        """Test searxng_url_str property strips trailing slash."""
        settings = Settings(searxng_url=HttpUrl("https://example.com/"))
        assert settings.searxng_url_str == "https://example.com"

    def test_settings_singleton(self):
        """Test that get_settings returns consistent instance."""
        # Note: get_settings() returns a new instance each call by default
        # This is acceptable behavior - settings should be immutable
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 == settings2

    def test_invalid_timeout(self):
        """Test that invalid timeout values are rejected."""
        with pytest.raises(ValueError):
            Settings(searxng_timeout=0)

        with pytest.raises(ValueError):
            Settings(searxng_timeout=400)

    def test_invalid_max_results(self):
        """Test that invalid max_results values are rejected."""
        with pytest.raises(ValueError):
            Settings(searxng_max_results=0)

        with pytest.raises(ValueError):
            Settings(searxng_max_results=200)

    def test_invalid_mcp_port(self):
        """Test that invalid port values are rejected."""
        with pytest.raises(ValueError):
            Settings(mcp_port=0)

        with pytest.raises(ValueError):
            Settings(mcp_port=70000)

    def test_invalid_mcp_transport(self):
        """Test that invalid transport values are rejected."""
        with pytest.raises(ValueError):
            Settings(mcp_transport="invalid")  # type: ignore

    def test_invalid_log_level(self):
        """Test that invalid log level values are rejected."""
        with pytest.raises(ValueError):
            Settings(log_level="invalid")  # type: ignore
