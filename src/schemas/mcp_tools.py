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
    access_level: Literal["public", "registered", "premium", "enterprise", "restricted"] = Field(
        ..., description="Requested access level"
    )
    requesting_interface: Optional[str] = Field(None, description="AI interface making the request")


class CheckContentAccessOutput(BaseModel):
    """Output schema for check_content_access MCP tool."""
    
    access_granted: bool = Field(..., description="Whether access is granted")
    access_level: str = Field(..., description="Actual access level granted")
    reason: Optional[str] = Field(None, description="Reason for access decision")
    access_token: Optional[str] = Field(None, description="Access token if granted")
    expires_at: Optional[str] = Field(None, description="Access expiration time (ISO format)")
    upgrade_required: Optional[bool] = Field(None, description="Whether subscription upgrade is needed")
    current_tier: Optional[str] = Field(None, description="User's current subscription tier")
    required_tier: Optional[str] = Field(None, description="Required subscription tier for access")
    pay_per_view_price: Optional[float] = Field(None, description="Pay-per-view price if available")


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
    access_level: Optional[str] = Field(None, description="Access level granted")
    amount_paid: Optional[float] = Field(None, description="Amount paid for access")
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


# Brand Metadata Management Schemas

class GetBrandMetadataInput(BaseModel):
    """Input schema for get_brand_metadata MCP tool."""
    
    publisher_id: str = Field(..., description="Publisher identifier")
    content_type: str = Field("article", description="Type of content (article, blog_post, etc.)")


class GetBrandMetadataOutput(BaseModel):
    """Output schema for get_brand_metadata MCP tool."""
    
    success: bool = Field(..., description="Whether the request was successful")
    publisher_id: Optional[str] = Field(None, description="Publisher identifier")
    content_type: Optional[str] = Field(None, description="Content type")
    brand_metadata: Optional[Dict[str, Any]] = Field(None, description="Complete brand metadata package")
    publisher_info: Optional[Dict[str, Any]] = Field(None, description="Publisher information")
    error: Optional[str] = Field(None, description="Error message if request failed")


class CreatePublisherProfileInput(BaseModel):
    """Input schema for create_publisher_profile MCP tool."""
    
    publisher_id: str = Field(..., description="Unique publisher identifier")
    name: str = Field(..., description="Publisher name")
    description: Optional[str] = Field(None, description="Publisher description")
    website: str = Field(..., description="Publisher website URL")
    contact_email: str = Field(..., description="Publisher contact email")
    logo_url: str = Field(..., description="Publisher logo URL")
    brand_color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Brand color in hex format")
    established_year: int = Field(..., ge=1400, le=2100, description="Year established")
    trust_score: float = Field(5.0, ge=0.0, le=10.0, description="Initial trust score")
    verified: bool = Field(False, description="Whether publisher is verified")
    editorial_standards_url: Optional[str] = Field(None, description="Editorial standards document URL")
    fact_checking_policy: Optional[str] = Field(None, description="Fact-checking policy description")
    default_attribution_requirements: Optional[Dict[str, Any]] = Field(None, description="Default attribution settings")
    content_licensing_terms: Optional[Dict[str, Any]] = Field(None, description="Content licensing terms")


class CreatePublisherProfileOutput(BaseModel):
    """Output schema for create_publisher_profile MCP tool."""
    
    success: bool = Field(..., description="Whether publisher was created successfully")
    publisher: Optional[Dict[str, Any]] = Field(None, description="Created publisher information")
    brand_analytics: Optional[Dict[str, Any]] = Field(None, description="Initial brand analytics")
    validation_warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    error: Optional[str] = Field(None, description="Error message if creation failed")
    validation_errors: List[str] = Field(default_factory=list, description="Validation errors")


class CalculateTrustScoreMetricsInput(BaseModel):
    """Input schema for calculate_trust_score_metrics MCP tool."""
    
    publisher_id: str = Field(..., description="Publisher identifier")
    fact_check_accuracy: float = Field(0.8, ge=0.0, le=1.0, description="Fact-checking accuracy rate")
    editorial_quality: float = Field(0.7, ge=0.0, le=1.0, description="Editorial quality score")
    source_reliability: float = Field(0.8, ge=0.0, le=1.0, description="Source reliability score")
    correction_rate: float = Field(0.1, ge=0.0, le=1.0, description="Content correction rate (lower is better)")
    reader_trust: float = Field(0.7, ge=0.0, le=1.0, description="Reader trust survey score")
    industry_recognition: float = Field(0.6, ge=0.0, le=1.0, description="Industry recognition score")
    transparency_score: float = Field(0.8, ge=0.0, le=1.0, description="Transparency and disclosure score")


class CalculateTrustScoreMetricsOutput(BaseModel):
    """Output schema for calculate_trust_score_metrics MCP tool."""
    
    success: bool = Field(..., description="Whether calculation was successful")
    publisher_id: Optional[str] = Field(None, description="Publisher identifier")
    publisher_name: Optional[str] = Field(None, description="Publisher name")
    trust_score_update: Optional[Dict[str, Any]] = Field(None, description="Trust score update information")
    calculation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed calculation breakdown")
    trust_trend: Optional[str] = Field(None, description="Trust score trend")
    score_history_length: Optional[int] = Field(None, description="Number of historical score records")
    error: Optional[str] = Field(None, description="Error message if calculation failed")


class GetPublisherAnalyticsInput(BaseModel):
    """Input schema for get_publisher_analytics MCP tool."""
    
    publisher_id: Optional[str] = Field(None, description="Publisher identifier (if None, returns global analytics)")


class GetPublisherAnalyticsOutput(BaseModel):
    """Output schema for get_publisher_analytics MCP tool."""
    
    success: bool = Field(..., description="Whether analytics retrieval was successful")
    analytics: Optional[Dict[str, Any]] = Field(None, description="Analytics data")
    timestamp: Optional[str] = Field(None, description="Analytics timestamp")
    error: Optional[str] = Field(None, description="Error message if retrieval failed")


class ListPublishersInput(BaseModel):
    """Input schema for list_publishers MCP tool."""
    
    include_analytics: bool = Field(True, description="Whether to include analytics summary")
    verified_only: bool = Field(False, description="Whether to return only verified publishers")


class ListPublishersOutput(BaseModel):
    """Output schema for list_publishers MCP tool."""
    
    success: bool = Field(..., description="Whether listing was successful")
    publishers: List[Dict[str, Any]] = Field(default_factory=list, description="List of publishers")
    total_count: int = Field(0, description="Total number of publishers")
    verified_count: int = Field(0, description="Number of verified publishers")
    average_trust_score: float = Field(0.0, description="Average trust score across all publishers")
    error: Optional[str] = Field(None, description="Error message if listing failed")


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
    },
    # Brand Metadata Management Tools
    "get_brand_metadata": {
        "input_schema": GetBrandMetadataInput,
        "output_schema": GetBrandMetadataOutput,
        "description": "Retrieve brand metadata package for a publisher and content type"
    },
    "create_publisher_profile": {
        "input_schema": CreatePublisherProfileInput,
        "output_schema": CreatePublisherProfileOutput,
        "description": "Create a new publisher profile with brand identity package"
    },
    "calculate_trust_score_metrics": {
        "input_schema": CalculateTrustScoreMetricsInput,
        "output_schema": CalculateTrustScoreMetricsOutput,
        "description": "Calculate and update trust score based on performance metrics"
    },
    "get_publisher_analytics": {
        "input_schema": GetPublisherAnalyticsInput,
        "output_schema": GetPublisherAnalyticsOutput,
        "description": "Get brand analytics and performance metrics for publishers"
    },
    "list_publishers": {
        "input_schema": ListPublishersInput,
        "output_schema": ListPublishersOutput,
        "description": "List all registered publishers with their information"
    }
}