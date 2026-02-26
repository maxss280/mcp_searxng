"""Manual testing script for MCP SearXNG server.

This script tests the SearXNG client directly without requiring the full MCP server.
Usage: python test_manual.py
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from mcp_searxng.client import SearXNGClient
from mcp_searxng.server import format_search_results


async def test_text_search():
    """Test basic text search."""
    print("=" * 60)
    print("TEST 1: Basic Text Search")
    print("=" * 60)
    
    async with SearXNGClient() as client:
        try:
            response = await client.search_text("python programming")
            formatted = await format_search_results(response)
            print(formatted)
            print("✅ Text search test PASSED\n")
            return True
        except Exception as e:
            print(f"❌ Text search test FAILED: {e}\n")
            return False


async def test_image_search():
    """Test image search."""
    print("=" * 60)
    print("TEST 2: Image Search")
    print("=" * 60)
    
    async with SearXNGClient() as client:
        try:
            response = await client.search(
                query="python logo",
                categories="images"
            )
            formatted = await format_search_results(response)
            print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
            print("✅ Image search test PASSED\n")
            return True
        except Exception as e:
            print(f"❌ Image search test FAILED: {e}\n")
            return False


async def test_video_search():
    """Test video search."""
    print("=" * 60)
    print("TEST 3: Video Search")
    print("=" * 60)
    
    async with SearXNGClient() as client:
        try:
            response = await client.search(
                query="python tutorial",
                categories="videos"
            )
            formatted = await format_search_results(response)
            print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
            print("✅ Video search test PASSED\n")
            return True
        except Exception as e:
            print(f"❌ Video search test FAILED: {e}\n")
            return False


async def test_pagination():
    """Test pagination."""
    print("=" * 60)
    print("TEST 4: Pagination (Page 2)")
    print("=" * 60)
    
    async with SearXNGClient() as client:
        try:
            response = await client.search_text("python", page=2)
            formatted = await format_search_results(response)
            print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
            print("✅ Pagination test PASSED\n")
            return True
        except Exception as e:
            print(f"❌ Pagination test FAILED: {e}\n")
            return False


async def test_error_handling():
    """Test error handling with invalid query."""
    print("=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)
    
    # This should work but return empty results
    async with SearXNGClient() as client:
        try:
            response = await client.search_text("xyzabc123noresults")
            formatted = await format_search_results(response)
            print(formatted)
            print("✅ Error handling test PASSED\n")
            return True
        except Exception as e:
            print(f"❌ Error handling test FAILED: {e}\n")
            return False


async def main():
    """Run all manual tests."""
    print("\n" + "=" * 60)
    print("MCP SEARXNG - MANUAL TESTING")
    print("=" * 60)
    print(f"SearXNG URL: https://searxng.pixelcrazed.com")
    print("=" * 60 + "\n")
    
    results = []
    
    # Run all tests
    results.append(("Text Search", await test_text_search()))
    results.append(("Image Search", await test_image_search()))
    results.append(("Video Search", await test_video_search()))
    results.append(("Pagination", await test_pagination()))
    results.append(("Error Handling", await test_error_handling()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
