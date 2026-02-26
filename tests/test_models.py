"""Tests for MCP SearXNG models."""

import pytest
from pydantic import HttpUrl

from mcp_searxng.models import SearchRequest, SearchResponse, SearchResult


class TestSearchResult:
    """Test cases for SearchResult model."""

    def test_basic_result(self):
        """Test creating a basic search result."""
        result = SearchResult(
            url=HttpUrl("https://example.com"),
            title="Example Page",
            content="This is an example",
            engine="google",
        )

        assert str(result.url) == "https://example.com/"
        assert result.title == "Example Page"
        assert result.content == "This is an example"
        assert result.engine == "google"
        assert result.score == 0.0
        assert result.category == "general"

    def test_result_with_optional_fields(self):
        """Test creating a result with all optional fields."""
        result = SearchResult(
            url=HttpUrl("https://example.com"),
            title="Example",
            content="Content",
            published_date="2024-01-01T00:00:00",
            thumbnail="https://example.com/thumb.jpg",
            engine="brave",
            engines=["brave", "google"],
            score=15.5,
            category="general",
        )

        assert result.published_date == "2024-01-01T00:00:00"
        assert result.thumbnail == "https://example.com/thumb.jpg"
        assert result.engines == ["brave", "google"]
        assert result.score == 15.5

    def test_result_from_dict(self):
        """Test creating a result from a dictionary."""
        data = {
            "url": "https://example.com",
            "title": "Example",
            "content": "Content",
            "publishedDate": "2024-01-01T00:00:00",
            "thumbnail": "https://example.com/thumb.jpg",
            "engine": "brave",
            "engines": ["brave", "google"],
            "score": 15.5,
            "category": "general",
        }

        result = SearchResult(**data)
        assert result.published_date == "2024-01-01T00:00:00"


class TestSearchResponse:
    """Test cases for SearchResponse model."""

    def test_empty_response(self):
        """Test creating an empty search response."""
        response = SearchResponse(query="test")

        assert response.query == "test"
        assert response.number_of_results == 0
        assert response.results == []
        assert response.suggestions == []
        assert response.corrections == []
        assert response.unresponsive_engines == []

    def test_response_with_results(self):
        """Test creating a response with results."""
        result = SearchResult(
            url=HttpUrl("https://example.com"),
            title="Example",
            content="Content",
            engine="google",
        )

        response = SearchResponse(
            query="test",
            number_of_results=1,
            results=[result],
            suggestions=["related1", "related2"],
        )

        assert len(response.results) == 1
        assert response.suggestions == ["related1", "related2"]

    def test_response_from_dict(self):
        """Test creating a response from a dictionary."""
        data = {
            "query": "python",
            "number_of_results": 2,
            "results": [
                {
                    "url": "https://python.org",
                    "title": "Python",
                    "content": "Python programming",
                    "engine": "google",
                }
            ],
            "suggestions": ["python tutorial", "python docs"],
            "unresponsive_engines": ["bing"],
        }

        response = SearchResponse(**data)
        assert response.query == "python"
        assert len(response.results) == 1
        assert response.unresponsive_engines == ["bing"]


class TestSearchRequest:
    """Test cases for SearchRequest model."""

    def test_basic_request(self):
        """Test creating a basic search request."""
        request = SearchRequest(q="python")

        assert request.q == "python"
        assert request.format == "json"
        assert request.categories == "general"
        assert request.pageno == 1
        assert request.safesearch == 1
        assert request.language is None
        assert request.time_range is None

    def test_request_with_filters(self):
        """Test creating a request with filters."""
        request = SearchRequest(
            q="python",
            pageno=2,
            language="en",
            time_range="month",
            safesearch=2,
            categories="images",
        )

        assert request.pageno == 2
        assert request.language == "en"
        assert request.time_range == "month"
        assert request.safesearch == 2
        assert request.categories == "images"

    def test_request_to_params(self):
        """Test converting request to parameters dict."""
        request = SearchRequest(
            q="python",
            pageno=2,
            language="en",
            time_range="month",
        )

        params = request.to_params()

        assert params["q"] == "python"
        assert params["pageno"] == 2
        assert params["language"] == "en"
        assert params["time_range"] == "month"
        assert params["format"] == "json"
        assert params["categories"] == "general"

    def test_request_to_params_without_optional(self):
        """Test converting request without optional fields."""
        request = SearchRequest(q="python")

        params = request.to_params()

        assert "language" not in params
        assert "time_range" not in params

    def test_invalid_page_number(self):
        """Test that page number must be at least 1."""
        with pytest.raises(ValueError):
            SearchRequest(q="test", pageno=0)

    def test_invalid_safesearch(self):
        """Test that safesearch must be 0, 1, or 2."""
        with pytest.raises(ValueError):
            SearchRequest(q="test", safesearch=3)

        with pytest.raises(ValueError):
            SearchRequest(q="test", safesearch=-1)

    def test_empty_query(self):
        """Test that empty query is rejected."""
        with pytest.raises(ValueError):
            SearchRequest(q="")
