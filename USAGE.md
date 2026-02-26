# MCP SearXNG - Usage Guide

This guide explains how to set up and use the MCP SearXNG server with opencode.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Options](#configuration-options)
3. [Using with opencode](#using-with-opencode)
4. [Docker Deployment](#docker-deployment)
5. [Local Development](#local-development)
6. [Available Tools](#available-tools)
7. [Troubleshooting](#troubleshooting)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp-searxng

# Copy the example environment file
cp .env.example .env

# Edit .env to configure your SearXNG instance
# Default: https://searxng.example.com

# Start the server
docker-compose up -d

# Server is now running on port 3000
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd mcp-searxng

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment file
cp .env.example .env

# Run the server
python -m mcp_searxng.server
```

## Configuration Options

Create a `.env` file with your settings:

```bash
# Required: SearXNG instance URL
SEARXNG_URL=https://searxng.example.com

# Optional: Request timeout (seconds)
SEARXNG_TIMEOUT=30

# Optional: Maximum results per query
SEARXNG_MAX_RESULTS=10

# Optional: Transport type (stdio or sse)
MCP_TRANSPORT=sse

# Optional: Server port (for SSE transport)
MCP_PORT=3000

# Optional: Logging level (debug, info, warning, error)
LOG_LEVEL=info
```

### Using Your Own SearXNG Instance

To use a different SearXNG instance:

```bash
# Edit .env
SEARXNG_URL=https://your-searxng-instance.com

# Or pass as environment variable
SEARXNG_URL=https://your-instance.com docker-compose up -d
```

Popular public instances:
- https://searx.example.com
- https://search.example.org
- https://searxng.example.net

## Using with opencode

### Step 1: Configure opencode

Add the MCP server to your opencode configuration. Edit your opencode config file (location varies by platform):

```json
{
  "mcpServers": {
    "searxng": {
      "command": "python",
      "args": ["-m", "mcp_searxng.server"],
      "cwd": "/path/to/mcp-searxng",
      "env": {
        "SEARXNG_URL": "https://searxng.example.com"
      }
    }
  }
}
```

### Step 2: Using Docker with opencode

If running via Docker:

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://localhost:3000/sse"
    }
  }
}
```

For remote Docker hosts, use the host IP or domain:

```json
{
  "mcpServers": {
    "searxng": {
      "url": "http://192.0.2.1:3000/sse"
    }
  }
}
```

### Step 3: Test in opencode

Once configured, you can ask opencode to search:

```
You: Search for Python programming tutorials
opencode: [Uses searxng_search tool]

You: Find images of Python logos
opencode: [Uses searxng_search_images tool]

You: Search for Python tutorial videos
opencode: [Uses searxng_search_videos tool]
```

## Docker Deployment

### Basic Usage

```bash
# Start the server
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the server
docker-compose down

# Restart with new configuration
docker-compose down && docker-compose up -d
```

### Custom Configuration

```bash
# Use a specific SearXNG instance
SEARXNG_URL=https://searx.be docker-compose up -d

# Change the port
MCP_PORT=8080 docker-compose up -d

# Full custom config
SEARXNG_URL=https://your-instance.com \
MCP_PORT=8080 \
SEARXNG_MAX_RESULTS=20 \
docker-compose up -d
```

### Docker Compose File Reference

```yaml
version: "3.8"

services:
  mcp-searxng:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: mcp-searxng-server
    restart: unless-stopped
    ports:
      - "${MCP_PORT:-3000}:3000"
    environment:
      - SEARXNG_URL=${SEARXNG_URL:-https://searxng.example.com}
      - SEARXNG_TIMEOUT=${SEARXNG_TIMEOUT:-30}
      - SEARXNG_MAX_RESULTS=${SEARXNG_MAX_RESULTS:-10}
      - MCP_TRANSPORT=${MCP_TRANSPORT:-sse}
      - MCP_PORT=3000
      - LOG_LEVEL=${LOG_LEVEL:-info}
```

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mcp_searxng --cov-report=html

# Run specific test file
pytest tests/test_client.py -v

# Run manual integration tests
python test_manual.py
```

### Code Quality

```bash
# Format code
black src tests

# Check formatting
black --check src tests

# Run linter
flake8 src tests
```

### Running the Server Locally

```bash
# Default (stdio transport)
python -m mcp_searxng.server

# With SSE transport
MCP_TRANSPORT=sse python -m mcp_searxng.server

# Custom port
MCP_TRANSPORT=sse MCP_PORT=8080 python -m mcp_searxng.server
```

## Available Tools

### 1. searxng_search

Search the web for text results.

**Parameters:**
- `query` (required): Search query string
- `page` (optional): Page number for pagination (default: 1)

**Example:**
```python
searxng_search("Python programming")
searxng_search("machine learning", page=2)
```

### 2. searxng_search_images

Search for images.

**Parameters:**
- `query` (required): Image search query
- `page` (optional): Page number for pagination (default: 1)

**Example:**
```python
searxng_search_images("Python logo")
searxng_search_images("cat photos", page=2)
```

### 3. searxng_search_videos

Search for videos.

**Parameters:**
- `query` (required): Video search query
- `page` (optional): Page number for pagination (default: 1)

**Example:**
```python
searxng_search_videos("Python tutorial")
searxng_search_videos("cooking recipes", page=3)
```

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to MCP server

**Solutions:**
1. Check if server is running:
   ```bash
   docker-compose ps
   ```

2. Check logs:
   ```bash
   docker-compose logs -f
   ```

3. Verify port is not in use:
   ```bash
   lsof -i :3000
   ```

### No Search Results

**Problem:** Search returns empty results

**Solutions:**
1. Check SearXNG URL is accessible:
   ```bash
   curl "${SEARXNG_URL}/search?q=test&format=json"
   ```

2. Try different search terms
3. Check SearXNG instance is not rate-limited

### Rate Limiting

**Problem:** Getting 429 or 503 errors

**Solutions:**
1. Reduce request frequency
2. Use multiple SearXNG instances
3. Check SEARXNG_TIMEOUT is appropriate (default: 30s)

### Docker Issues

**Problem:** Container won't start

**Solutions:**
1. Rebuild the image:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. Check environment variables:
   ```bash
   docker-compose config
   ```

### opencode Integration Issues

**Problem:** opencode cannot see the MCP tools

**Solutions:**
1. Verify MCP server config is correct JSON
2. Check server is running before starting opencode
3. Try using stdio transport instead of SSE:
   ```json
   {
     "mcpServers": {
       "searxng": {
         "command": "python",
         "args": ["-m", "mcp_searxng.server"],
         "cwd": "/path/to/mcp-searxng"
       }
     }
   }
   ```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `SEARXNG_URL` | `https://searxng.example.com` | SearXNG instance URL |
| `SEARXNG_TIMEOUT` | `30` | HTTP request timeout in seconds |
| `SEARXNG_MAX_RESULTS` | `10` | Maximum results per query |
| `MCP_TRANSPORT` | `stdio` | Transport type: `stdio` or `sse` |
| `MCP_PORT` | `3000` | Server port for SSE transport |
| `LOG_LEVEL` | `info` | Logging level: `debug`, `info`, `warning`, `error` |

## Getting Help

1. Check the logs: `docker-compose logs -f`
2. Run tests: `pytest tests/ -v`
3. Test manually: `python test_manual.py`
4. Review configuration: `docker-compose config`

## Next Steps

- See [PROJECTS.md](PROJECTS.md) for roadmap and future phases
- Check [README.md](README.md) for project overview
- Review the code in `src/mcp_searxng/` for implementation details
