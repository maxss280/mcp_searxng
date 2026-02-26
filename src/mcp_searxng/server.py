"""MCP SearXNG server implementation."""

import logging
import sys

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from mcp.server.transport_security import TransportSecuritySettings

from mcp_searxng.client import SearXNGClient
from mcp_searxng.config import get_settings
from mcp_searxng.models import SearchResponse


def setup_logging() -> None:
    """Configure logging for the application."""
    settings = get_settings()
    log_level = getattr(logging, settings.log_level.upper())

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )


mcp = FastMCP("searxng")
logger = logging.getLogger(__name__)


async def format_search_results(response: SearchResponse, max_content_len: int = 150) -> str:
    if not response.results:
        return f"No results: {response.query}"

    parts = [f"Results for: {response.query}\n(Launch parallel subagents to webfetch top 3-5 URLs and synthesize relevant info)\n"]
    for i, r in enumerate(response.results, 1):
        content = (r.content[:max_content_len] + "...") if r.content and len(r.content) > max_content_len else (r.content or "")
        parts.append(f"{i}. {r.title}\n   URL: {r.url}\n   {content}")
    
    if response.suggestions:
        parts.append(f"\nRelated: {', '.join(response.suggestions[:3])}")
    
    return "\n\n".join(parts)


@mcp.tool()
async def searxng_search(query: str, page: int = 1) -> str:
    """
    Search the web using SearXNG metasearch engine.

    Returns search results with titles, URLs, and short snippets.
    IMPORTANT: For comprehensive answers, launch parallel subagents to 
    webfetch the top 3-5 relevant URLs and synthesize only the significant 
    information relevant to the user's query. Discard irrelevant content.

    Args:
        query: The search query string (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted search results with titles, URLs, and snippets

    Example:
        searxng_search("python programming")
        searxng_search("machine learning", page=2)
    """
    logger.info(f"Search request: {query} (page {page})")

    async with SearXNGClient() as client:
        try:
            response = await client.search_text(query=query, page=page)
            return await format_search_results(response)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search failed: {str(e)}"


@mcp.tool()
async def searxng_search_images(query: str, page: int = 1) -> str:
    """
    Search for images using SearXNG metasearch engine.

    Returns image results with thumbnails and metadata.
    Use webfetch on relevant URLs to get full image details.

    Args:
        query: The image search query (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted image search results with thumbnails and metadata

    Example:
        searxng_search_images("python logo")
    """
    logger.info(f"Image search request: {query} (page {page})")

    async with SearXNGClient() as client:
        try:
            response = await client.search(
                query=query,
                page=page,
                categories="images",
            )
            return await format_search_results(response)
        except Exception as e:
            logger.error(f"Image search failed: {e}")
            return f"Image search failed: {str(e)}"


@mcp.tool()
async def searxng_search_videos(query: str, page: int = 1) -> str:
    """
    Search for videos using SearXNG metasearch engine.

    Returns video results with thumbnails and metadata.
    Use webfetch on relevant URLs to get full video details.

    Args:
        query: The video search query (required)
        page: Page number for pagination (default: 1)

    Returns:
        Formatted video search results with thumbnails and metadata

    Example:
        searxng_search_videos("python tutorial")
    """
    logger.info(f"Video search request: {query} (page {page})")

    async with SearXNGClient() as client:
        try:
            response = await client.search(
                query=query,
                page=page,
                categories="videos",
            )
            return await format_search_results(response)
        except Exception as e:
            logger.error(f"Video search failed: {e}")
            return f"Video search failed: {str(e)}"


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

        async def handle_sse(request):
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
