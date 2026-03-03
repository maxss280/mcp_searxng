"""MCP SearXNG server implementation."""

import logging
import sys
from typing import Tuple

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.transport_security import TransportSecuritySettings

from mcp_searxng.client import SearXNGClient
from mcp_searxng.config import get_settings
from mcp_searxng.models import SearchResponse

# Constants
DEFAULT_MAX_CONTENT_LENGTH = 150
MAX_QUERY_LENGTH = 500

logger = logging.getLogger(__name__)
mcp = FastMCP("searxng")


def setup_logging() -> None:
    """Configure logging for the application."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper())

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


def validate_query(query: str) -> Tuple[bool, str]:
    """Validate search query.

    Args:
        query: The search query string to validate

    Returns:
        Tuple of (is_valid, result_or_error_message)
        If valid, result contains the sanitized query
        If invalid, result contains the error message
    """
    if not query:
        return False, "Query cannot be empty"

    query = query.strip()
    if not query:
        return False, "Query cannot be whitespace only"

    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Query too long (max {MAX_QUERY_LENGTH} characters)"

    # Remove null bytes (potential injection)
    query = query.replace("\x00", "")

    return True, query


async def _perform_search(
    query: str, page: int = 1, categories: str = "general"
) -> str:
    """Perform a search query and format results.

    Args:
        query: The search query string (already validated)
        page: Page number for pagination
        categories: Search category (general, images, videos)

    Returns:
        Formatted search results or error message
    """
    logger.info(f"Search request: {query} (page {page}, category: {categories})")

    async with SearXNGClient() as client:
        try:
            if categories == "general":
                response = await client.search_text(query=query, page=page)
            else:
                response = await client.search(
                    query=query,
                    page=page,
                    categories=categories,
                )
            return await format_search_results(response)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}"


async def format_search_results(
    response: SearchResponse, max_content_len: int = DEFAULT_MAX_CONTENT_LENGTH
) -> str:
    """Format search results for display.

    Args:
        response: Search response from SearXNG
        max_content_len: Maximum length of content snippet

    Returns:
        Formatted string with search results
    """
    if not response.results:
        return f"No results: {response.query}"

    parts = [
        f"Results for: {response.query}\n"
        "(Launch parallel subagents to webfetch top 3-5 URLs and synthesize info)\n"
    ]
    for i, r in enumerate(response.results, 1):
        content = (
            (r.content[:max_content_len] + "...")
            if r.content and len(r.content) > max_content_len
            else (r.content or "")
        )
        parts.append(f"{i}. {r.title}\n   URL: {r.url}\n   {content}")

    if response.suggestions:
        parts.append(f"\nRelated: {', '.join(response.suggestions[:3])}")

    return "\n\n".join(parts)


@mcp.tool()
async def searxng_search(query: str, page: int = 1) -> str:
    """
    Search the web using SearXNG metasearch engine.

    Returns search results with titles, URLs, and short snippets.

    Args:
        query: The search query string (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted search results with titles, URLs, and snippets

    Example:
        searxng_search("python programming")
        searxng_search("machine learning", page=2)
    """
    is_valid, result = validate_query(query)
    if not is_valid:
        return f"Invalid query: {result}"
    query = result

    return await _perform_search(query, page, "general")


@mcp.tool()
async def searxng_search_images(query: str, page: int = 1) -> str:
    """
    Search for images using SearXNG metasearch engine.

    Returns image search results with thumbnails and metadata.

    Args:
        query: The image search query (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted image search results with thumbnails and metadata

    Example:
        searxng_search_images("python logo")
    """
    is_valid, result = validate_query(query)
    if not is_valid:
        return f"Invalid query: {result}"
    query = result

    return await _perform_search(query, page, "images")


@mcp.tool()
async def searxng_search_videos(query: str, page: int = 1) -> str:
    """
    Search for videos using SearXNG metasearch engine.

    Returns video search results with thumbnails and metadata.

    Args:
        query: The video search query (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted video search results with thumbnails and metadata

    Example:
        searxng_search_videos("python tutorial")
    """
    is_valid, result = validate_query(query)
    if not is_valid:
        return f"Invalid query: {result}"
    query = result

    return await _perform_search(query, page, "videos")


def main() -> None:
    """Run the MCP server."""
    setup_logging()
    settings = get_settings()

    logger.info("Starting MCP SearXNG server")
    logger.info(f"SearXNG URL: {settings.searxng_url_str}")
    logger.info(f"Transport: {settings.mcp_transport}")

    if settings.mcp_transport == "stdio":
        mcp.run(transport="stdio")
    else:
        import uvicorn
        from starlette.applications import Starlette
        from starlette.routing import Route, Mount
        from starlette.responses import Response

        security_settings = TransportSecuritySettings(
            enable_dns_rebinding_protection=False
        )
        sse = SseServerTransport("/messages/", security_settings=security_settings)

        async def handle_sse(request):  # type: ignore
            async with sse.connect_sse(
                request.scope, request.receive, request._send
            ) as streams:
                await mcp._mcp_server.run(
                    streams[0],
                    streams[1],
                    mcp._mcp_server.create_initialization_options(),
                )
            return Response()

        app = Starlette(
            routes=[
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Mount("/messages/", app=sse.handle_post_message),
            ]
        )
        uvicorn.run(app, host="0.0.0.0", port=settings.mcp_port)


if __name__ == "__main__":
    main()
