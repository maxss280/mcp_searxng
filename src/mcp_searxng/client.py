"""SearXNG HTTP client implementation."""

import logging
from typing import Optional

import httpx

from mcp_searxng.config import Settings, get_settings
from mcp_searxng.models import SearchRequest, SearchResponse

logger = logging.getLogger(__name__)


class SearXNGClient:
    """HTTP client for SearXNG API."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initialize the client with settings."""
        self.settings = settings or get_settings()
        self.base_url = self.settings.searxng_url_str
        self.timeout = self.settings.searxng_timeout
        self.max_results = self.settings.searxng_max_results
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                headers={
                    "User-Agent": "MCP-SearXNG/0.1.0",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        query: str,
        page: int = 1,
        **kwargs,
    ) -> SearchResponse:
        """
        Perform a search query against SearXNG.

        Args:
            query: The search query string
            page: Page number for pagination
            **kwargs: Additional search parameters

        Returns:
            SearchResponse with results

        Raises:
            httpx.HTTPStatusError: If the request fails
            httpx.TimeoutException: If the request times out
        """
        request = SearchRequest(
            q=query,
            pageno=page,
            **kwargs,
        )

        client = await self._get_client()
        url = f"{self.base_url}/search"

        logger.debug(f"Searching SearXNG: {query} (page {page})")

        try:
            response = await client.get(
                url,
                params=request.to_params(),
            )
            response.raise_for_status()
            data = response.json()

            search_response = SearchResponse(**data)

            # Filter out invalid results (missing URL or title)
            valid_results = search_response.get_valid_results()
            
            # Limit results if needed
            if len(valid_results) > self.max_results:
                valid_results = valid_results[:self.max_results]
            
            search_response.results = valid_results

            logger.info(
                f"Search completed: {query} - "
                f"{len(search_response.results)} results"
            )

            return search_response

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error searching SearXNG: {e.response.status_code} - "
                f"{e.response.text}"
            )
            raise
        except httpx.TimeoutException:
            logger.error(f"Timeout searching SearXNG: {query}")
            raise

    async def search_text(
        self,
        query: str,
        page: int = 1,
    ) -> SearchResponse:
        """
        Perform a text search query.

        Args:
            query: The search query string
            page: Page number for pagination

        Returns:
            SearchResponse with text results
        """
        return await self.search(
            query=query,
            page=page,
            categories="general",
        )

    async def __aenter__(self) -> "SearXNGClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.close()
