"""
Main entry point for the Content Publishing MCP Server.

This module provides the main function and CLI interface for running
the MCP server for content monetization and brand preservation.
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional

from .server import mcp_server


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Content Publishing MCP Server for brand preservation and monetization"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Content Publishing MCP Server 0.1.0"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Display server information and exit"
    )
    
    return parser.parse_args()


async def main() -> None:
    """Main entry point for the MCP server."""
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Display server info if requested
    if args.info:
        server_info = mcp_server.get_server_info()
        print("Content Publishing MCP Server Information:")
        print(f"  Name: {server_info['name']}")
        print(f"  Version: {server_info['version']}")
        print(f"  Description: {server_info['description']}")
        print(f"  Available Tools: {server_info['tools_count']}")
        print(f"  Tools: {', '.join(server_info['available_tools'])}")
        return
    
    try:
        logger.info("Starting Content Publishing MCP Server...")
        await mcp_server.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)


def cli_main() -> None:
    """CLI entry point that handles asyncio setup."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()