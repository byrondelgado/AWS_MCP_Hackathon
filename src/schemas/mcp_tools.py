"""
MCP tool schemas for content access and brand preservation.

These schemas define the input/output structures for MCP tools
as specified in the design document.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class GetBrandedContentInput(BaseModel):
    """Input schema for get_branded_content MCP tool."""
    
    content_id: str = Field(..., description="Unique identifier for the content")
    requesting_interface: Literal["chatgpt", "claude", "gemini", "other"] = Field(
        ..., description="AI interface requesting the content"
    )
    display_capabilities: Dict[str, bool] = Field(
        default_factory=lambda: {
            "supports_badges": True,
            "supports_rich_formatting": True,
            "supports_interactive_elements": True
        },
        description="Display capabilities of the requesting interface"
    )
    user_id: Optional[str] = Field(None, description="User identifier for access control")


class GetBrandedContentOutput(BaseModel):
    """Output schema for get_branded_content MCP tool."""
    
    success: bool = Field(..., description="Whether the request was successful")
    content: Optional[Dict[str, Any]] = Field(None, description="Content data with brand metadata")
    error_message: Optional[str] = Field(None, description="Error message if request failed")
    access_level: str = Field("free", description="Access level granted")


class CheckContentAccessInput(BaseModel):
    """Input schema for check_content_access MCP tool."""
    
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    access_level: Literal["free", "premium", "enterprise"] = Field(
        ..., description="Requested access level"
    )


class CheckContentAccessOutput(BaseModel):
    """Output schema for check_content_access MCP tool."""
    
    access_granted: bool = Field(..., description="Whether access is granted")
    access_level: str = Field(..., description="Actual access level granted")
    reason: Optional[str] = Field(None, description="Reason for access decision")
    expires_at: Optional[str] = Field(None, description="Access expiration time (ISO format)")


class GrantTemporaryAccessInput(BaseModel):
    """Input schema for grant_temporary_access MCP tool."""
    
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    duration: int = Field(..., ge=60, le=86400, description="Access duration in seconds (1 min to 24 hours)")
    payment_token: Optional[str] = Field(None, description="Payment verification token")


class GrantTemporaryAccessOutput(BaseModel):
    """Output schema for grant_temporary_access MCP tool."""
    
    access_granted: bool = Field(..., description="Whether temporary access was granted")
    access_token: Optional[str] = Field(None, description="Temporary access token")
    expires_at: Optional[str] = Field(None, description="Access expiration time (ISO format)")
    error_message: Optional[str] = Field(None, description="Error message if access denied")


class ValidateAttributionInput(BaseModel):
    """Input schema for validate_attribution MCP tool."""
    
    content_id: str = Field(..., description="Content identifier")
    displayed_attribution: str = Field(..., description="Attribution text as displayed")
    display_format: str = Field(..., description="Format used for attribution display")
    visibility_duration: Optional[int] = Field(None, description="Duration attribution was visible (seconds)")


class ValidateAttributionOutput(BaseModel):
    """Output schema for validate_attribution MCP tool."""
    
    compliant: bool = Field(..., description="Whether attribution meets requirements")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    violations: List[str] = Field(default_factory=list, description="List of compliance violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class TrackBrandVisibilityInput(BaseModel):
    """Input schema for track_brand_visibility MCP tool."""
    
    content_id: str = Field(..., description="Content identifier")
    interface: str = Field(..., description="AI interface where content was displayed")
    visibility_metrics: Dict[str, Any] = Field(
        ..., description="Visibility metrics (duration, prominence, etc.)"
    )
    user_interactions: List[Dict[str, Any]] = Field(
        default_factory=list, description="User interactions with brand elements"
    )


class TrackBrandVisibilityOutput(BaseModel):
    """Output schema for track_brand_visibility MCP tool."""
    
    tracking_recorded: bool = Field(..., description="Whether tracking was successfully recorded")
    tracking_id: str = Field(..., description="Unique tracking identifier")
    compliance_status: str = Field(..., description="Current compliance status")


class CalculateTrustScoreInput(BaseModel):
    """Input schema for calculate_trust_score MCP tool."""
    
    publisher_id: str = Field(..., description="Publisher identifier")
    content_id: Optional[str] = Field(None, description="Specific content identifier")
    metrics_period: Literal["day", "week", "month", "year"] = Field(
        "month", description="Time period for metrics calculation"
    )


class CalculateTrustScoreOutput(BaseModel):
    """Output schema for calculate_trust_score MCP tool."""
    
    trust_score: float = Field(..., ge=0.0, le=10.0, description="Calculated trust score")
    score_components: Dict[str, float] = Field(
        ..., description="Breakdown of trust score components"
    )
    trend: Literal["increasing", "stable", "decreasing"] = Field(
        ..., description="Trust score trend"
    )
    last_updated: str = Field(..., description="Last update timestamp (ISO format)")


class AnalyzeEngagementInput(BaseModel):
    """Input schema for analyze_engagement MCP tool."""
    
    content_id: Optional[str] = Field(None, description="Specific content identifier")
    publisher_id: Optional[str] = Field(None, description="Publisher identifier")
    time_range: Dict[str, str] = Field(
        ..., description="Time range for analysis (start_date, end_date in ISO format)"
    )
    metrics: List[str] = Field(
        default_factory=lambda: ["views", "shares", "engagement_time", "brand_interactions"],
        description="Metrics to analyze"
    )


class AnalyzeEngagementOutput(BaseModel):
    """Output schema for analyze_engagement MCP tool."""
    
    engagement_metrics: Dict[str, Any] = Field(..., description="Calculated engagement metrics")
    trends: Dict[str, str] = Field(..., description="Trend analysis for each metric")
    insights: List[str] = Field(default_factory=list, description="Key insights from analysis")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")


class CalculateDynamicPricingInput(BaseModel):
    """Input schema for calculate_dynamic_pricing MCP tool."""
    
    content_id: str = Field(..., description="Content identifier")
    user_profile: Dict[str, Any] = Field(..., description="User profile for personalization")
    market_conditions: Dict[str, Any] = Field(
        default_factory=dict, description="Current market conditions"
    )
    demand_factors: Dict[str, Any] = Field(
        default_factory=dict, description="Demand influencing factors"
    )


class CalculateDynamicPricingOutput(BaseModel):
    """Output schema for calculate_dynamic_pricing MCP tool."""
    
    base_price: float = Field(..., ge=0.0, description="Base content price")
    dynamic_price: float = Field(..., ge=0.0, description="Calculated dynamic price")
    price_factors: Dict[str, float] = Field(..., description="Factors affecting price calculation")
    discount_available: bool = Field(False, description="Whether discount is available")
    pricing_tier: str = Field(..., description="Pricing tier applied")


class ProcessSubscriptionInput(BaseModel):
    """Input schema for process_subscription MCP tool."""
    
    user_id: str = Field(..., description="User identifier")
    subscription_tier: Literal["free", "premium", "enterprise"] = Field(
        ..., description="Subscription tier"
    )
    payment_method: Dict[str, Any] = Field(..., description="Payment method details")
    billing_cycle: Literal["monthly", "annual"] = Field("monthly", description="Billing cycle")


class ProcessSubscriptionOutput(BaseModel):
    """Output schema for process_subscription MCP tool."""
    
    subscription_created: bool = Field(..., description="Whether subscription was created")
    subscription_id: Optional[str] = Field(None, description="Subscription identifier")
    next_billing_date: Optional[str] = Field(None, description="Next billing date (ISO format)")
    error_message: Optional[str] = Field(None, description="Error message if subscription failed")


class GenerateComplianceReportInput(BaseModel):
    """Input schema for generate_compliance_report MCP tool."""
    
    publisher_id: Optional[str] = Field(None, description="Publisher identifier")
    content_id: Optional[str] = Field(None, description="Content identifier")
    report_period: Dict[str, str] = Field(
        ..., description="Report period (start_date, end_date in ISO format)"
    )
    report_type: Literal["attribution", "brand_visibility", "revenue", "comprehensive"] = Field(
        "comprehensive", description="Type of compliance report"
    )


class GenerateComplianceReportOutput(BaseModel):
    """Output schema for generate_compliance_report MCP tool."""
    
    report_generated: bool = Field(..., description="Whether report was generated")
    report_url: Optional[str] = Field(None, description="URL to download the report")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Report summary")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Overall compliance score")


# MCP Tool Registry
MCP_TOOL_SCHEMAS = {
    "get_branded_content": {
        "input_schema": GetBrandedContentInput,
        "output_schema": GetBrandedContentOutput,
        "description": "Retrieve content with full brand metadata and attribution requirements"
    },
    "check_content_access": {
        "input_schema": CheckContentAccessInput,
        "output_schema": CheckContentAccessOutput,
        "description": "Verify user access rights for specific content"
    },
    "grant_temporary_access": {
        "input_schema": GrantTemporaryAccessInput,
        "output_schema": GrantTemporaryAccessOutput,
        "description": "Provide time-limited access to premium content"
    },
    "validate_attribution": {
        "input_schema": ValidateAttributionInput,
        "output_schema": ValidateAttributionOutput,
        "description": "Validate attribution compliance for displayed content"
    },
    "track_brand_visibility": {
        "input_schema": TrackBrandVisibilityInput,
        "output_schema": TrackBrandVisibilityOutput,
        "description": "Track brand visibility and user engagement metrics"
    },
    "calculate_trust_score": {
        "input_schema": CalculateTrustScoreInput,
        "output_schema": CalculateTrustScoreOutput,
        "description": "Calculate publisher or content trust score"
    },
    "analyze_engagement": {
        "input_schema": AnalyzeEngagementInput,
        "output_schema": AnalyzeEngagementOutput,
        "description": "Analyze user engagement metrics and trends"
    },
    "calculate_dynamic_pricing": {
        "input_schema": CalculateDynamicPricingInput,
        "output_schema": CalculateDynamicPricingOutput,
        "description": "Calculate dynamic pricing for content based on demand and user profile"
    },
    "process_subscription": {
        "input_schema": ProcessSubscriptionInput,
        "output_schema": ProcessSubscriptionOutput,
        "description": "Process user subscription for premium content access"
    },
    "generate_compliance_report": {
        "input_schema": GenerateComplianceReportInput,
        "output_schema": GenerateComplianceReportOutput,
        "description": "Generate compliance reports for attribution and brand visibility"
    }
}