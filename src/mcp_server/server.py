"""
MCP Server implementation for content publishing and brand preservation.

This module implements the core MCP server with tool registration,
protocol handlers, and server initialization logic.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import ValidationError

try:
    # Try relative imports first (for when running as module)
    from ..schemas.mcp_tools import MCP_TOOL_SCHEMAS
    from ..models.content import BrandedContentResponse, ContentAccessRequest
    from ..models.brand import BrandMetadata, ComplianceTracking
    from .tools import ContentTools, BrandTools, AnalyticsTools, PricingTools
    from .config import get_config, is_tool_enabled
except ImportError:
    # Fall back to direct imports (for standalone execution)
    from schemas.mcp_tools import MCP_TOOL_SCHEMAS
    from models.content import BrandedContentResponse, ContentAccessRequest
    from models.brand import BrandMetadata, ComplianceTracking
    from mcp_server.tools import ContentTools, BrandTools, AnalyticsTools, PricingTools
    from mcp_server.config import get_config, is_tool_enabled


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentPublishingMCPServer:
    """MCP Server for content publishing and brand preservation."""
    
    def __init__(self):
        """Initialize the MCP server with tools and handlers."""
        self.config = get_config()
        self.server = Server(self.config.server_name)
        self.content_tools = ContentTools()
        self.brand_tools = BrandTools()
        self.analytics_tools = AnalyticsTools()
        self.pricing_tools = PricingTools()
        
        # Register MCP protocol handlers
        self._register_handlers()
        
        logger.info("Content Publishing MCP Server initialized")
    
    def _register_handlers(self) -> None:
        """Register MCP protocol handlers for tools and resources."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available MCP tools."""
            tools = []
            
            for tool_name, tool_config in MCP_TOOL_SCHEMAS.items():
                # Check if tool is enabled
                if not is_tool_enabled(tool_name):
                    continue
                
                # Convert Pydantic schema to MCP tool schema
                input_schema = tool_config["input_schema"].model_json_schema()
                
                tool = Tool(
                    name=tool_name,
                    description=tool_config["description"],
                    inputSchema=input_schema
                )
                tools.append(tool)
            
            logger.info(f"Listed {len(tools)} available tools")
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str, 
            arguments: Optional[Dict[str, Any]] = None
        ) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle MCP tool calls."""
            
            if arguments is None:
                arguments = {}
            
            logger.info(f"Tool called: {name} with arguments: {arguments}")
            
            try:
                # Route tool calls to appropriate handlers
                result = await self._route_tool_call(name, arguments)
                
                # Return result as TextContent
                return [TextContent(
                    type="text",
                    text=str(result) if not isinstance(result, str) else result
                )]
                
            except ValidationError as e:
                error_msg = f"Validation error for tool {name}: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=error_msg)]
                
            except Exception as e:
                error_msg = f"Error executing tool {name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(type="text", text=error_msg)]
    
    async def _route_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Route tool calls to appropriate tool handlers."""
        
        # Validate input arguments against schema
        if tool_name not in MCP_TOOL_SCHEMAS:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        input_schema = MCP_TOOL_SCHEMAS[tool_name]["input_schema"]
        validated_input = input_schema(**arguments)
        
        # Route to appropriate tool handler
        if tool_name == "get_branded_content":
            return await self.content_tools.get_branded_content(validated_input)
        
        elif tool_name == "check_content_access":
            return await self.content_tools.check_content_access(validated_input)
        
        elif tool_name == "grant_temporary_access":
            return await self.content_tools.grant_temporary_access(validated_input)
        
        elif tool_name == "validate_attribution":
            return await self.brand_tools.validate_attribution(validated_input)
        
        elif tool_name == "track_brand_visibility":
            return await self.brand_tools.track_brand_visibility(validated_input)
        
        elif tool_name == "calculate_trust_score":
            return await self.analytics_tools.calculate_trust_score(validated_input)
        
        elif tool_name == "analyze_engagement":
            return await self.analytics_tools.analyze_engagement(validated_input)
        
        elif tool_name == "calculate_dynamic_pricing":
            return await self.pricing_tools.calculate_dynamic_pricing(validated_input)
        
        elif tool_name == "process_subscription":
            return await self.pricing_tools.process_subscription(validated_input)
        
        elif tool_name == "generate_compliance_report":
            return await self.analytics_tools.generate_compliance_report(validated_input)
        
        # Brand Metadata Management Tools
        elif tool_name == "get_brand_metadata":
            return await self.brand_tools.get_brand_metadata(
                validated_input.publisher_id, 
                validated_input.content_type
            )
        
        elif tool_name == "create_publisher_profile":
            return await self.brand_tools.create_publisher_profile(validated_input.model_dump())
        
        elif tool_name == "calculate_trust_score_metrics":
            metrics = {
                "fact_check_accuracy": validated_input.fact_check_accuracy,
                "editorial_quality": validated_input.editorial_quality,
                "source_reliability": validated_input.source_reliability,
                "correction_rate": validated_input.correction_rate,
                "reader_trust": validated_input.reader_trust,
                "industry_recognition": validated_input.industry_recognition,
                "transparency_score": validated_input.transparency_score
            }
            return await self.brand_tools.calculate_trust_score(validated_input.publisher_id, metrics)
        
        elif tool_name == "get_publisher_analytics":
            return await self.brand_tools.get_publisher_analytics(validated_input.publisher_id)
        
        elif tool_name == "list_publishers":
            return await self.brand_tools.list_publishers()
        
        else:
            raise ValueError(f"Tool handler not implemented: {tool_name}")
    
    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        logger.info("Starting Content Publishing MCP Server...")
        
        # Initialize server options
        init_options = InitializationOptions(
            server_name=self.config.server_name,
            server_version=self.config.server_version
        )
        
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    init_options
                )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information and status."""
        enabled_tools = [tool for tool in MCP_TOOL_SCHEMAS.keys() if is_tool_enabled(tool)]
        return {
            "name": self.config.server_name,
            "version": self.config.server_version,
            "description": self.config.server_description,
            "tools_count": len(enabled_tools),
            "available_tools": enabled_tools,
            "status": "running",
            "timestamp": datetime.utcnow().isoformat()
        }


# Global server instance
mcp_server = ContentPublishingMCPServer()


async def main():
    """Main entry point for the MCP server."""
    await mcp_server.run()


if __name__ == "__main__":
    asyncio.run(main())