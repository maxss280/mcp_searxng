"""Tests for MCP SearXNG HTTP client."""

import httpx
import pytest
import respx
from pydantic import HttpUrl

from mcp_searxng.client import SearXNGClient
from mcp_searxng.config import Settings
from mcp_searxng.models import SearchResponse


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        searxng_url=HttpUrl("https://test.searxng.com"),
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


class TestSearXNGClient:
    """Test cases for SearXNGClient."""

    @respx.mock
    async def test_search_success(self, mock_settings, sample_search_response):
        """Test successful search request."""
        # Mock the SearXNG API endpoint
        route = respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            response = await client.search("python")

        assert isinstance(response, SearchResponse)
        assert response.query == "python"
        assert len(response.results) == 2
        assert response.results[0].title == "Python Programming"

        # Verify the request was made with correct parameters
        assert route.called
        request = route.calls[0].request
        assert "q=python" in str(request.url)
        assert "format=json" in str(request.url)

    @respx.mock
    async def test_search_with_pagination(self, mock_settings, sample_search_response):
        """Test search with pagination."""
        route = respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            await client.search("python", page=3)

        request = route.calls[0].request
        assert "pageno=3" in str(request.url)

    @respx.mock
    async def test_search_with_categories(self, mock_settings, sample_search_response):
        """Test search with category filter."""
        route = respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            await client.search("python", categories="images")

        request = route.calls[0].request
        assert "categories=images" in str(request.url)

    @respx.mock
    async def test_search_text_method(self, mock_settings, sample_search_response):
        """Test search_text convenience method."""
        route = respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            response = await client.search_text("python", page=1)

        assert isinstance(response, SearchResponse)
        request = route.calls[0].request
        assert "categories=general" in str(request.url)

    @respx.mock
    async def test_search_http_error(self, mock_settings):
        """Test handling of HTTP errors."""
        respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            with pytest.raises(httpx.HTTPStatusError):
                await client.search("python")

    @respx.mock
    async def test_search_timeout(self, mock_settings):
        """Test handling of timeout errors."""
        respx.get("https://test.searxng.com/search").mock(
            side_effect=httpx.TimeoutException("Request timed out")
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            with pytest.raises(httpx.TimeoutException):
                await client.search("python")

    @respx.mock
    async def test_max_results_limit(self, mock_settings):
        """Test that results are limited to max_results."""
        # Create response with more results than max_results
        response_data = {
            "query": "python",
            "number_of_results": 10,
            "results": [
                {
                    "url": f"https://example{i}.com",
                    "title": f"Result {i}",
                    "content": f"Content {i}",
                    "engine": "google",
                }
                for i in range(10)
            ],
            "suggestions": [],
        }

        respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            response = await client.search("python")

        assert len(response.results) == 5  # Limited by max_results setting

    async def test_client_context_manager(self, mock_settings):
        """Test async context manager properly closes client."""
        client = SearXNGClient(settings=mock_settings)

        assert client._client is None

        async with client:
            client._client = httpx.AsyncClient()
            assert client._client is not None

        # After exiting context, client should be closed
        assert client._client is None

    @respx.mock
    async def test_client_reuses_connection(
        self, mock_settings, sample_search_response
    ):
        """Test that client reuses HTTP connection."""
        respx.get("https://test.searxng.com/search").mock(
            return_value=httpx.Response(200, json=sample_search_response)
        )

        client = SearXNGClient(settings=mock_settings)

        async with client:
            await client.search("python")
            await client.search("java")
            # Client should still be active within context
            assert client._client is not None
            assert not client._client.is_closed

    def test_client_initialization(self, mock_settings):
        """Test client initialization with settings."""
        client = SearXNGClient(settings=mock_settings)

        assert client.base_url == "https://test.searxng.com"
        assert client.timeout == 10
        assert client.max_results == 5

    def test_client_default_settings(self):
        """Test client uses default settings when none provided."""
        client = SearXNGClient()

        assert client.base_url == "https://searxng.pixelcrazed.com"
        assert client.timeout == 30
        assert client.max_results == 10
