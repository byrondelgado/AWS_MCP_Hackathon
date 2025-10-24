"""
Brand metadata models for content publishing MCP server.

These models define the structure for brand preservation and attribution
requirements as specified in the design document.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
import re


class PublisherMetadata(BaseModel):
    """Publisher brand information and identity."""
    
    name: str = Field(..., description="Publisher name (e.g., 'The Guardian')")
    logo: HttpUrl = Field(..., description="URL to publisher logo/badge")
    brand_color: str = Field(..., description="Brand color in hex format", pattern=r"^#[0-9A-Fa-f]{6}$")
    trust_score: float = Field(..., ge=0.0, le=10.0, description="Trust score from 0-10")
    established_year: int = Field(..., ge=1400, le=2100, description="Year publisher was established")
    website: Optional[HttpUrl] = Field(None, description="Publisher website URL")
    
    @field_validator('trust_score')
    @classmethod
    def validate_trust_score(cls, v):
        """Ensure trust score is within valid range with proper precision."""
        return round(v, 1)


class AttributionRequirements(BaseModel):
    """Attribution and display requirements for content."""
    
    required: bool = Field(True, description="Whether attribution is mandatory")
    display_format: Literal["badge-with-logo", "text-only", "minimal", "full"] = Field(
        ..., description="Required display format for attribution"
    )
    minimum_visibility: Literal["prominent", "standard", "minimal"] = Field(
        ..., description="Minimum visibility level required"
    )
    linkback: HttpUrl = Field(..., description="URL for attribution linkback")
    duration_seconds: Optional[int] = Field(None, ge=1, description="Minimum display duration in seconds")


class EditorialMetadata(BaseModel):
    """Editorial standards and verification information."""
    
    fact_checked: bool = Field(False, description="Whether content has been fact-checked")
    fact_check_date: Optional[datetime] = Field(None, description="Date of fact-checking")
    editorial_standards: Optional[HttpUrl] = Field(None, description="URL to editorial standards document")
    journalist_credentials: List[str] = Field(default_factory=list, description="Journalist credentials and experience")
    verification_level: Literal["single-sourced", "double-sourced", "triple-sourced", "peer-reviewed"] = Field(
        "single-sourced", description="Level of source verification"
    )
    editorial_process: Optional[str] = Field(None, description="Editorial process description")


class RightsMetadata(BaseModel):
    """Content rights and usage permissions."""
    
    usage: Literal["ai-training-permitted", "ai-training-restricted", "summary-only", "no-ai"] = Field(
        ..., description="AI usage permissions"
    )
    attribution: Literal["mandatory", "optional", "none"] = Field(
        "mandatory", description="Attribution requirements"
    )
    modification: Literal["summary-only", "excerpts-allowed", "no-modification", "full-modification"] = Field(
        "summary-only", description="Allowed content modifications"
    )
    commercial_use: Literal["licensed", "restricted", "prohibited"] = Field(
        "licensed", description="Commercial usage permissions"
    )
    territory_restrictions: List[str] = Field(default_factory=list, description="Restricted territories (ISO country codes)")
    embargo_date: Optional[datetime] = Field(None, description="Content embargo date")


class ContentCuration(BaseModel):
    """Content curation and classification metadata."""
    
    content_type: str = Field(..., description="Type of content (e.g., 'investigative-journalism')")
    expertise: List[str] = Field(default_factory=list, description="Areas of expertise covered")
    verification_level: str = Field("standard", description="Content verification level")
    editorial_process: Optional[str] = Field(None, description="Editorial process used")
    subject_codes: List[str] = Field(default_factory=list, description="BISAC/BIC/Thema subject codes")
    keywords: List[str] = Field(default_factory=list, description="Content keywords")


class DisplayRequirements(BaseModel):
    """Display requirements for AI interfaces."""
    
    badges: List[str] = Field(default_factory=list, description="Required badges to display")
    minimum_attribution: str = Field(..., description="Minimum attribution text required")
    brand_visibility: Literal["high-prominence", "standard", "minimal"] = Field(
        "standard", description="Required brand visibility level"
    )
    interactive_elements: Dict[str, bool] = Field(
        default_factory=dict, description="Allowed interactive elements"
    )


class BrandMetadata(BaseModel):
    """Complete brand metadata package for content."""
    
    publisher: PublisherMetadata
    attribution: AttributionRequirements
    editorial: EditorialMetadata
    rights: RightsMetadata
    curation: ContentCuration
    display_requirements: DisplayRequirements
    
    # Tracking and compliance
    metadata_version: str = Field("1.0", description="Brand metadata schema version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ComplianceTracking(BaseModel):
    """Compliance tracking for brand visibility and attribution."""
    
    tracking_id: str = Field(..., description="Unique tracking identifier")
    required_metrics: List[str] = Field(default_factory=list, description="Required metrics to track")
    reporting_endpoint: HttpUrl = Field(..., description="Endpoint for compliance reporting")
    tracking_start: datetime = Field(default_factory=datetime.utcnow)
    minimum_visibility_duration: Optional[int] = Field(None, description="Minimum visibility duration in seconds")