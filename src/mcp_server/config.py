"""
Configuration management for the Content Publishing MCP Server.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ServerConfig:
    """MCP Server configuration."""
    
    # Server identification
    server_name: str = "content-publishing-mcp-server"
    server_version: str = "0.1.0"
    server_description: str = "MCP server for content monetization and brand preservation"
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Tool configuration
    enable_all_tools: bool = True
    disabled_tools: list = None
    
    # Storage configuration (for demo/development)
    use_in_memory_storage: bool = True
    data_directory: Optional[Path] = None
    
    # AWS configuration (for production)
    aws_region: str = "us-east-1"
    dynamodb_table_prefix: str = "content-mcp"
    s3_bucket_name: Optional[str] = None
    
    # Security configuration
    enable_authentication: bool = False
    api_key_header: str = "X-API-Key"
    
    def __post_init__(self):
        """Post-initialization setup."""
        if self.disabled_tools is None:
            self.disabled_tools = []
        
        if self.data_directory is None:
            self.data_directory = Path.home() / ".content-mcp" / "data"


class ConfigManager:
    """Manages server configuration from environment variables and files."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self._config = None
    
    def get_config(self) -> ServerConfig:
        """Get server configuration, loading from environment if needed."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> ServerConfig:
        """Load configuration from environment variables."""
        config = ServerConfig()
        
        # Server configuration
        config.server_name = os.getenv("MCP_SERVER_NAME", config.server_name)
        config.log_level = os.getenv("MCP_LOG_LEVEL", config.log_level)
        
        # Tool configuration
        config.enable_all_tools = os.getenv("MCP_ENABLE_ALL_TOOLS", "true").lower() == "true"
        
        disabled_tools_env = os.getenv("MCP_DISABLED_TOOLS", "")
        if disabled_tools_env:
            config.disabled_tools = [tool.strip() for tool in disabled_tools_env.split(",")]
        
        # Storage configuration
        config.use_in_memory_storage = os.getenv("MCP_USE_IN_MEMORY_STORAGE", "true").lower() == "true"
        
        data_dir_env = os.getenv("MCP_DATA_DIRECTORY")
        if data_dir_env:
            config.data_directory = Path(data_dir_env)
        
        # AWS configuration
        config.aws_region = os.getenv("AWS_REGION", config.aws_region)
        config.dynamodb_table_prefix = os.getenv("MCP_DYNAMODB_PREFIX", config.dynamodb_table_prefix)
        config.s3_bucket_name = os.getenv("MCP_S3_BUCKET")
        
        # Security configuration
        config.enable_authentication = os.getenv("MCP_ENABLE_AUTH", "false").lower() == "true"
        config.api_key_header = os.getenv("MCP_API_KEY_HEADER", config.api_key_header)
        
        return config
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        config = self.get_config()
        
        if not config.enable_all_tools:
            return False
        
        return tool_name not in config.disabled_tools
    
    def get_aws_config(self) -> Dict[str, Any]:
        """Get AWS-specific configuration."""
        config = self.get_config()
        
        return {
            "region": config.aws_region,
            "dynamodb_table_prefix": config.dynamodb_table_prefix,
            "s3_bucket_name": config.s3_bucket_name
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        config = self.get_config()
        
        return {
            "use_in_memory": config.use_in_memory_storage,
            "data_directory": config.data_directory
        }


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> ServerConfig:
    """Get the current server configuration."""
    return config_manager.get_config()


def is_tool_enabled(tool_name: str) -> bool:
    """Check if a tool is enabled in the current configuration."""
    return config_manager.is_tool_enabled(tool_name)