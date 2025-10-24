"""
Content models for the publishing MCP server.

These models define the structure for articles, publishers, and content
with embedded brand metadata.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, HttpUrl, field_validator, ConfigDict
from enum import Enum

from .brand import BrandMetadata, ComplianceTracking


class ContentType(str, Enum):
    """Supported content types."""
    ARTICLE = "article"
    BLOG_POST = "blog_post"
    NEWS_REPORT = "news_report"
    OPINION = "opinion"
    REVIEW = "review"
    INTERVIEW = "interview"
    FEATURE = "feature"
    BREAKING_NEWS = "breaking_news"


class ContentStatus(str, Enum):
    """Content publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    EMBARGOED = "embargoed"
    RESTRICTED = "restricted"


class Author(BaseModel):
    """Content author information."""
    
    name: str = Field(..., description="Author full name")
    email: Optional[str] = Field(None, description="Author email address")
    bio: Optional[str] = Field(None, description="Author biography")
    credentials: List[str] = Field(default_factory=list, description="Author credentials and qualifications")
    social_links: Dict[str, HttpUrl] = Field(default_factory=dict, description="Social media links")
    author_id: Optional[str] = Field(None, description="Unique author identifier")


class ContentMetrics(BaseModel):
    """Content engagement and performance metrics."""
    
    views: int = Field(0, ge=0, description="Total content views")
    shares: int = Field(0, ge=0, description="Total shares across platforms")
    engagement_score: float = Field(0.0, ge=0.0, le=10.0, description="Engagement score 0-10")
    reading_time_minutes: Optional[int] = Field(None, ge=1, description="Estimated reading time")
    word_count: Optional[int] = Field(None, ge=0, description="Content word count")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class Article(BaseModel):
    """Article content with brand metadata."""
    
    # Core content
    content_id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Article title")
    subtitle: Optional[str] = Field(None, max_length=1000, description="Article subtitle")
    text: str = Field(..., min_length=1, description="Full article text content")
    summary: Optional[str] = Field(None, max_length=2000, description="Article summary/excerpt")
    
    # Metadata
    content_type: ContentType = Field(ContentType.ARTICLE, description="Type of content")
    status: ContentStatus = Field(ContentStatus.DRAFT, description="Publication status")
    language: str = Field("en", description="Content language (ISO 639-1 code)")
    
    # Publishing info
    publish_date: Optional[datetime] = Field(None, description="Publication date")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Author and source
    authors: List[Author] = Field(default_factory=list, description="Article authors")
    source_url: Optional[HttpUrl] = Field(None, description="Original source URL")
    
    # Brand and attribution
    brand_metadata: BrandMetadata = Field(..., description="Complete brand metadata package")
    
    # Performance metrics
    metrics: Optional[ContentMetrics] = Field(None, description="Content performance metrics")
    
    # Tags and categorization
    tags: List[str] = Field(default_factory=list, description="Content tags")
    categories: List[str] = Field(default_factory=list, description="Content categories")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    @field_validator('language')
    @classmethod
    def validate_language_code(cls, v):
        """Validate ISO 639-1 language code format."""
        if not v or len(v) != 2 or not v.isalpha():
            raise ValueError("Language must be a valid ISO 639-1 two-letter code")
        return v.lower()


class Publisher(BaseModel):
    """Publisher profile and configuration."""
    
    publisher_id: str = Field(..., description="Unique publisher identifier")
    name: str = Field(..., description="Publisher name")
    description: Optional[str] = Field(None, description="Publisher description")
    
    # Contact and identity
    website: HttpUrl = Field(..., description="Publisher website")
    contact_email: str = Field(..., description="Publisher contact email")
    logo_url: HttpUrl = Field(..., description="Publisher logo URL")
    
    # Brand configuration
    brand_color: str = Field(..., pattern=r"^#[0-9A-Fa-f]{6}$", description="Brand color in hex")
    established_year: int = Field(..., ge=1400, le=2100, description="Year established")
    
    # Trust and verification
    trust_score: float = Field(5.0, ge=0.0, le=10.0, description="Publisher trust score")
    verified: bool = Field(False, description="Whether publisher is verified")
    verification_date: Optional[datetime] = Field(None, description="Date of verification")
    
    # Editorial standards
    editorial_standards_url: Optional[HttpUrl] = Field(None, description="Editorial standards document URL")
    fact_checking_policy: Optional[str] = Field(None, description="Fact-checking policy description")
    
    # Configuration
    default_attribution_requirements: Dict[str, Any] = Field(
        default_factory=dict, description="Default attribution settings"
    )
    content_licensing_terms: Dict[str, Any] = Field(
        default_factory=dict, description="Content licensing terms"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class BrandedContentResponse(BaseModel):
    """Response format for branded content delivery via MCP."""
    
    content: Article = Field(..., description="Article content with metadata")
    brand_package: BrandMetadata = Field(..., description="Brand metadata package")
    compliance_tracking: ComplianceTracking = Field(..., description="Compliance tracking information")
    
    # Interface-specific formatting
    display_elements: List[Dict[str, Any]] = Field(
        default_factory=list, description="Interface-specific display elements"
    )
    interaction_options: List[Dict[str, Any]] = Field(
        default_factory=list, description="Available user interaction options"
    )
    
    # Access control
    access_level: str = Field("free", description="Content access level")
    access_expires_at: Optional[datetime] = Field(None, description="Access expiration time")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ContentAccessRequest(BaseModel):
    """Request for content access verification."""
    
    user_id: str = Field(..., description="Requesting user identifier")
    content_id: str = Field(..., description="Requested content identifier")
    access_level: str = Field("free", description="Requested access level")
    requesting_interface: str = Field(..., description="AI interface making the request")
    
    # Interface capabilities
    display_capabilities: Dict[str, bool] = Field(
        default_factory=dict, description="Interface display capabilities"
    )
    
    # Request context
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_subscription_tier: Optional[str] = Field(None, description="User subscription tier")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )