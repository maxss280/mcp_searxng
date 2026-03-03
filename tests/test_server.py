"""Tests for MCP SearXNG server."""

import httpx
import pytest
import respx
from pydantic import HttpUrl

from mcp_searxng.config import Settings
from mcp_searxng.models import SearchResponse
from mcp_searxng.server import format_search_results


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        searxng_url=HttpUrl("https://searxng.pixelcrazed.com"),
        searxng_timeout=10,
        searxng_max_results=5,
    )


@pytest.fixture
def sample_search_response():
    """Create a sample search response."""
    return {
        "query": "python",
        "number_of_results": 2,
        "results": [
            {
                "url": "https://python.org",
                "title": "Python Programming",
                "content": "Official Python site",
                "engine": "google",
                "engines": ["google", "brave"],
                "score": 20.0,
                "category": "general",
            },
            {
                "url": "https://pypi.org",
                "title": "PyPI",
                "content": "Python Package Index",
                "engine": "google",
                "score": 15.0,
                "category": "general",
            },
        ],
        "suggestions": ["python tutorial", "python docs"],
        "corrections": [],
        "unresponsive_engines": [],
    }


class TestFormatSearchResults:
    """Test cases for format_search_results function."""

    async def test_format_with_results(self):
        """Test formatting response with results."""
        response = SearchResponse(
            query="python",
            number_of_results=2,
            results=[
                {
                    "url": "https://python.org",
                    "title": "Python",
                    "content": "Official site",
                    "engine": "google",
                },
                {
                    "url": "https://pypi.org",
                    "title": "PyPI",
                    "content": "Package Index",
                    "engine": "google",
                },
            ],
            suggestions=["python tutorial"],
        )

        formatted = await format_search_results(response)

        assert "Results for: python" in formatted
        assert "1. Python" in formatted
        assert "2. PyPI" in formatted
        assert "https://python.org" in formatted
        assert "https://pypi.org" in formatted
        assert "Related:" in formatted
        assert "python tutorial" in formatted

    async def test_format_empty_results(self):
        """Test formatting response with no results."""
        response = SearchResponse(query="xyzabc123")

        formatted = await format_search_results(response)

        assert "No results: xyzabc123" in formatted

    async def test_format_without_suggestions(self):
        """Test formatting without suggestions."""
        response = SearchResponse(
            query="test",
            results=[
                {
                    "url": "https://example.com",
                    "title": "Example",
                    "content": "Content",
                    "engine": "google",
                }
            ],
        )

        formatted = await format_search_results(response)

        assert "Example" in formatted
        assert "Related:" not in formatted


class TestSearxngSearch:
    """Test cases for searxng_search tool."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_success(
        self, mock_settings, sample_search_response, monkeypatch
    ):
        """Test successful search via MCP tool."""
        respx.get("https://searxng.pixelcrazed.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        from mcp_searxng.server import searxng_search

        result = await searxng_search("python")

        assert "Results for: python" in result
        assert "Python Programming" in result
        assert "PyPI" in result

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, mock_settings, sample_search_response, monkeypatch
    ):
        """Test search with page parameter."""
        route = respx.get("https://searxng.pixelcrazed.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        from mcp_searxng.server import searxng_search

        await searxng_search("python", page=2)

        request = route.calls[0].request
        assert "pageno=2" in str(request.url)

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_error_handling(self, mock_settings, monkeypatch):
        """Test error handling in search tool."""
        respx.get("https://searxng.pixelcrazed.com/search").mock(
            return_value=httpx.Response(500, text="Server Error")
        )

        from mcp_searxng.server import searxng_search

        result = await searxng_search("python")

        assert "Search failed:" in result

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_timeout_handling(self, mock_settings, monkeypatch):
        """Test timeout error handling in search tool."""
        respx.get("https://searxng.pixelcrazed.com/search").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        from mcp_searxng.server import searxng_search

        result = await searxng_search("python")

        assert "Search failed:" in result

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_empty_query_validation(self, mock_settings, monkeypatch):
        """Test empty query validation."""
        from mcp_searxng.server import searxng_search

        result = await searxng_search("")

        assert "Invalid query" in result
        assert "empty" in result.lower()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_whitespace_query_validation(self, mock_settings, monkeypatch):
        """Test whitespace-only query validation."""
        from mcp_searxng.server import searxng_search

        result = await searxng_search("   ")

        assert "Invalid query" in result
        assert "whitespace" in result.lower()

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_too_long_query_validation(self, mock_settings, monkeypatch):
        """Test query length validation."""
        from mcp_searxng.server import searxng_search

        long_query = "a" * 501
        result = await searxng_search(long_query)

        assert "Invalid query" in result
        assert "too long" in result.lower()


class TestServerIntegration:
    """Integration tests for the MCP server."""

    def test_server_initialization(self):
        """Test that the MCP server can be imported."""
        from mcp_searxng.server import mcp

        assert mcp.name == "searxng"

    def test_setup_logging(self):
        """Test logging setup function."""
        import logging

        from mcp_searxng.server import setup_logging

        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level in [logging.INFO, logging.DEBUG, logging.WARNING]
