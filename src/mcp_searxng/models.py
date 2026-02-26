"""Pydantic models for SearXNG API requests and responses."""

from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class SearchResult(BaseModel):
    """Individual search result item."""

    model_config = ConfigDict(populate_by_name=True)

    url: Optional[HttpUrl] = Field(
        default=None,
        description="Result URL",
    )
    title: str = Field(default="", description="Page title")
    content: Optional[str] = Field(
        default="",
        description="Search snippet/description",
    )
    published_date: Optional[str] = Field(
        default=None,
        alias="publishedDate",
        description="Publication date if available",
    )
    thumbnail: Optional[str] = Field(
        default=None,
        description="Thumbnail URL if available",
    )
    engine: str = Field(default="", description="Primary search engine")
    engines: List[str] = Field(
        default_factory=list,
        description="All engines that returned this result",
    )
    score: float = Field(default=0.0, description="Relevance score")
    category: str = Field(default="general", description="Result category")

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, v: Any) -> Any:
        """Convert empty strings to None."""
        if v == "" or v is None:
            return None
        return v

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        """Convert None to empty string."""
        if v is None:
            return ""
        return v

    def is_valid(self) -> bool:
        """Check if result has minimum required fields."""
        if self.url is None:
            return False
        url_str = str(self.url).strip()
        return bool(self.title) and bool(url_str)


class SearchResponse(BaseModel):
    """SearXNG search API response."""

    model_config = ConfigDict(populate_by_name=True)

    query: str = Field(description="Search query")
    number_of_results: int = Field(
        default=0,
        description="Total number of results",
    )
    results: List[SearchResult] = Field(
        default_factory=list,
        description="Search results",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Related search suggestions",
    )
    corrections: List[str] = Field(
        default_factory=list,
        description="Spelling corrections",
    )
    unresponsive_engines: List[str] = Field(
        default_factory=list,
        description="Engines that didn't respond",
    )

    @field_validator("unresponsive_engines", mode="before")
    @classmethod
    def validate_unresponsive_engines(cls, v: Any) -> Any:
        """Handle unresponsive_engines being a list of lists/strings."""
        if not isinstance(v, list):
            return []
        result = []
        for item in v:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, list) and len(item) > 0:
                # If it's a list like ['artic', 'parsing error'], 
                # take the first element (engine name)
                result.append(str(item[0]))
        return result

    def get_valid_results(self) -> List[SearchResult]:
        """Get only valid results (with URL and title)."""
        return [r for r in self.results if r.is_valid()]


class SearchRequest(BaseModel):
    """SearXNG search request parameters."""

    q: str = Field(description="Search query", min_length=1)
    format: str = Field(default="json", description="Response format")
    categories: str = Field(default="general", description="Search categories")
    pageno: int = Field(default=1, ge=1, description="Page number")
    language: Optional[str] = Field(default=None, description="Language code")
    time_range: Optional[str] = Field(
        default=None,
        description="Time filter (day, month, year)",
    )
    safesearch: int = Field(
        default=1,
        ge=0,
        le=2,
        description="Safe search level (0=off, 1=moderate, 2=strict)",
    )

    def to_params(self) -> dict[str, Any]:
        """Convert to dictionary for HTTP request."""
        params: dict[str, Any] = {
            "q": self.q,
            "format": self.format,
            "categories": self.categories,
            "pageno": self.pageno,
            "safesearch": self.safesearch,
        }
        if self.language:
            params["language"] = self.language
        if self.time_range:
            params["time_range"] = self.time_range
        return params
