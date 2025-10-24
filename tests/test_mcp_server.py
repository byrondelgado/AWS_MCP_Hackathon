"""
Tests for MCP server foundation and basic functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.mcp_server.server import ContentPublishingMCPServer
from src.mcp_server.config import ServerConfig, ConfigManager
from src.schemas.mcp_tools import MCP_TOOL_SCHEMAS


class TestMCPServerFoundation:
    """Test MCP server foundation implementation."""
    
    def test_server_initialization(self):
        """Test that MCP server initializes correctly."""
        server = ContentPublishingMCPServer()
        
        # Check server components are initialized
        assert server.server is not None
        assert server.content_tools is not None
        assert server.brand_tools is not None
        assert server.analytics_tools is not None
        assert server.pricing_tools is not None
        assert server.config is not None
    
    def test_server_info(self):
        """Test server information retrieval."""
        server = ContentPublishingMCPServer()
        info = server.get_server_info()
        
        # Check required info fields
        assert "name" in info
        assert "version" in info
        assert "description" in info
        assert "tools_count" in info
        assert "available_tools" in info
        assert "status" in info
        assert "timestamp" in info
        
        # Check values
        assert info["status"] == "running"
        assert isinstance(info["tools_count"], int)
        assert isinstance(info["available_tools"], list)
    
    def test_tool_schemas_loaded(self):
        """Test that MCP tool schemas are properly loaded."""
        # Check that schemas are available
        assert len(MCP_TOOL_SCHEMAS) > 0
        
        # Check required tools are present
        required_tools = [
            "get_branded_content",
            "check_content_access", 
            "validate_attribution",
            "track_brand_visibility"
        ]
        
        for tool in required_tools:
            assert tool in MCP_TOOL_SCHEMAS
            assert "input_schema" in MCP_TOOL_SCHEMAS[tool]
            assert "output_schema" in MCP_TOOL_SCHEMAS[tool]
            assert "description" in MCP_TOOL_SCHEMAS[tool]
    
    @pytest.mark.asyncio
    async def test_tool_routing(self):
        """Test that tool calls are routed correctly."""
        server = ContentPublishingMCPServer()
        
        # Test routing to content tools
        with patch.object(server.content_tools, 'get_branded_content') as mock_tool:
            mock_tool.return_value = {"success": True}
            
            # This would normally be called through MCP protocol
            # Testing the routing logic directly
            result = await server._route_tool_call("get_branded_content", {
                "content_id": "test-content",
                "requesting_interface": "chatgpt"
            })
            
            mock_tool.assert_called_once()
    
    def test_config_manager(self):
        """Test configuration manager functionality."""
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        # Check config is ServerConfig instance
        assert isinstance(config, ServerConfig)
        
        # Check default values
        assert config.server_name == "content-publishing-mcp-server"
        assert config.server_version == "0.1.0"
        assert config.enable_all_tools is True
        assert config.use_in_memory_storage is True
    
    def test_tool_enablement(self):
        """Test tool enablement configuration."""
        from src.mcp_server.config import is_tool_enabled
        
        # Test that tools are enabled by default
        assert is_tool_enabled("get_branded_content") is True
        assert is_tool_enabled("check_content_access") is True
        assert is_tool_enabled("nonexistent_tool") is True  # Default behavior
    
    @pytest.mark.asyncio
    async def test_invalid_tool_call(self):
        """Test handling of invalid tool calls."""
        server = ContentPublishingMCPServer()
        
        # Test unknown tool
        with pytest.raises(ValueError, match="Unknown tool"):
            await server._route_tool_call("unknown_tool", {})
    
    def test_server_protocol_handlers_registered(self):
        """Test that MCP protocol handlers are registered."""
        server = ContentPublishingMCPServer()
        
        # Check that server object exists and is properly initialized
        assert server.server is not None
        assert hasattr(server.server, 'list_tools')
        assert hasattr(server.server, 'call_tool')


class TestMCPToolIntegration:
    """Test integration between MCP server and tool implementations."""
    
    @pytest.mark.asyncio
    async def test_get_branded_content_integration(self):
        """Test get_branded_content tool integration."""
        server = ContentPublishingMCPServer()
        
        # Test with valid input
        result = await server._route_tool_call("get_branded_content", {
            "content_id": "guardian-climate-2024",
            "requesting_interface": "chatgpt"
        })
        
        # Check result structure
        assert hasattr(result, 'success')
        if result.success:
            assert hasattr(result, 'content')
            assert hasattr(result, 'access_level')
    
    @pytest.mark.asyncio
    async def test_check_content_access_integration(self):
        """Test check_content_access tool integration."""
        server = ContentPublishingMCPServer()
        
        # Test with valid input
        result = await server._route_tool_call("check_content_access", {
            "user_id": "test_user",
            "content_id": "guardian-climate-2024",
            "access_level": "free"
        })
        
        # Check result structure
        assert hasattr(result, 'access_granted')
        assert hasattr(result, 'access_level')
        assert isinstance(result.access_granted, bool)


if __name__ == "__main__":
    pytest.main([__file__])