"""
MCP tool schemas for content access and brand preservation.

This package contains Pydantic schemas for MCP tool inputs and outputs
as specified in the design document.
"""

from .mcp_tools import (
    # Input schemas
    GetBrandedContentInput,
    CheckContentAccessInput,
    GrantTemporaryAccessInput,
    ValidateAttributionInput,
    TrackBrandVisibilityInput,
    CalculateTrustScoreInput,
    AnalyzeEngagementInput,
    CalculateDynamicPricingInput,
    ProcessSubscriptionInput,
    GenerateComplianceReportInput,
    
    # Output schemas
    GetBrandedContentOutput,
    CheckContentAccessOutput,
    GrantTemporaryAccessOutput,
    ValidateAttributionOutput,
    TrackBrandVisibilityOutput,
    CalculateTrustScoreOutput,
    AnalyzeEngagementOutput,
    CalculateDynamicPricingOutput,
    ProcessSubscriptionOutput,
    GenerateComplianceReportOutput,
    
    # Registry
    MCP_TOOL_SCHEMAS
)

__all__ = [
    # Input schemas
    "GetBrandedContentInput",
    "CheckContentAccessInput", 
    "GrantTemporaryAccessInput",
    "ValidateAttributionInput",
    "TrackBrandVisibilityInput",
    "CalculateTrustScoreInput",
    "AnalyzeEngagementInput",
    "CalculateDynamicPricingInput",
    "ProcessSubscriptionInput",
    "GenerateComplianceReportInput",
    
    # Output schemas
    "GetBrandedContentOutput",
    "CheckContentAccessOutput",
    "GrantTemporaryAccessOutput", 
    "ValidateAttributionOutput",
    "TrackBrandVisibilityOutput",
    "CalculateTrustScoreOutput",
    "AnalyzeEngagementOutput",
    "CalculateDynamicPricingOutput",
    "ProcessSubscriptionOutput",
    "GenerateComplianceReportOutput",
    
    # Registry
    "MCP_TOOL_SCHEMAS"
]