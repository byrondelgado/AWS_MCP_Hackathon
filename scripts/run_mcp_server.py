#!/usr/bin/env python3
"""
MCP Server runner for the Content Publishing MCP Server.

This script runs the MCP server in stdio mode for integration with MCP clients.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.server import ContentPublishingMCPServer


async def main():
    """Run the MCP server."""
    print("🚀 Starting Content Publishing MCP Server...", file=sys.stderr)
    print("Server ready for MCP connections.", file=sys.stderr)
    
    server = ContentPublishingMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())