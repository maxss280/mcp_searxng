# MCP SearXNG

A Model Context Protocol (MCP) server that enables AI assistants to search the web using SearXNG metasearch engine.

## Features

- **Web Search**: Search the web with SearXNG's privacy-focused metasearch
- **Image Search**: Find images across multiple search engines (Inprogress)
- **Video Search**: Search for videos with metadata (Inprogress)
- **Docker Support**: Easy deployment with Docker Compose
- **Configurable**: Works with any SearXNG instance

## Quick Start

### Using Docker Compose

```bash
# Clone the repository
git clone <repo-url>
cd mcp-searxng

# Copy and configure environment
cp .env_example .env
# Edit .env to set your SearXNG URL

# Run with Docker Compose
docker-compose up -d
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run the server
python -m mcp_searxng.server
```

## Configuration

Environment variables (set in `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_URL` | `https://searxng.example.com` | SearXNG instance URL |
| `SEARXNG_TIMEOUT` | `30` | Request timeout (seconds) |
| `SEARXNG_MAX_RESULTS` | `10` | Max results per query |
| `MCP_TRANSPORT` | `stdio` | Transport: `stdio` or `sse` |
| `MCP_PORT` | `3000` | Server port (for SSE) |
| `LOG_LEVEL` | `info` | Logging level |

## MCP Tools

### searxng_search

Search the web for text results.

```python
searxng_search("python programming")
searxng_search("machine learning", page=2)
```

### searxng_search_images

Search for images.

```python
searxng_search_images("python logo")
```

### searxng_search_videos

Search for videos.

```python
searxng_search_videos("python tutorial")
```

## Development

```bash
# Run linting
flake8 src tests
black --check src tests

# Format code
black src tests

# Run tests with coverage
pytest --cov=mcp_searxng --cov-report=html
```

## License

MIT License

See [LICENSE](LICENSE) for full text.

## Acknowledgments

This project uses open source software. See [ACKNOWLEDGMENTS.md](ACKNOWLEDGMENTS.md) for a full list of dependencies and their licenses.
