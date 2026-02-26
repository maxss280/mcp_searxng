"""MCP SearXNG package."""

__version__ = "0.1.0"
__all__ = ["SearXNGClient", "SearchResponse", "SearchResult", "Settings"]

from mcp_searxng.client import SearXNGClient
from mcp_searxng.config import Settings
from mcp_searxng.models import SearchResponse, SearchResult
