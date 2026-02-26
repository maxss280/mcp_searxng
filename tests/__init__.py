"""Test package initialization."""

from mcp_searxng import SearXNGClient, SearchResponse, SearchResult, Settings


def test_version():
    """Test version is defined."""
    from mcp_searxng import __version__

    assert __version__ == "0.1.0"


def test_exports():
    """Test that main classes are exported."""
    assert SearXNGClient is not None
    assert SearchResponse is not None
    assert SearchResult is not None
    assert Settings is not None
