"""
Access control models for content gating and subscription management.

These models define subscription tiers, access tokens, and content value assessment.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum
import secrets


class SubscriptionTier(str, Enum):
    """Subscription tier levels."""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class AccessLevel(str, Enum):
    """Content access levels."""
    PUBLIC = "public"
    REGISTERED = "registered"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"
    RESTRICTED = "restricted"


class ContentValueTier(str, Enum):
    """Content value classification."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"


class SubscriptionPlan(BaseModel):
    """Subscription plan definition."""
    
    tier: SubscriptionTier = Field(..., description="Subscription tier")
    name: str = Field(..., description="Plan display name")
    description: str = Field(..., description="Plan description")
    
    # Pricing
    price_monthly: float = Field(..., ge=0, description="Monthly price in USD")
    price_annual: Optional[float] = Field(None, ge=0, description="Annual price in USD")
    
    # Access rights
    allowed_access_levels: List[AccessLevel] = Field(
        default_factory=list, description="Content access levels included"
    )
    content_limit: Optional[int] = Field(None, ge=0, description="Monthly content access limit")
    
    # Features
    features: List[str] = Field(default_factory=list, description="Plan features")
    priority_support: bool = Field(False, description="Priority customer support")
    api_access: bool = Field(False, description="API access enabled")
    
    # Metadata
    is_active: bool = Field(True, description="Whether plan is currently offered")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class UserSubscription(BaseModel):
    """User subscription information."""
    
    user_id: str = Field(..., description="User identifier")
    subscription_tier: SubscriptionTier = Field(..., description="Current subscription tier")
    plan_id: str = Field(..., description="Subscription plan identifier")
    
    # Status
    status: Literal["active", "cancelled", "expired", "suspended"] = Field(
        "active", description="Subscription status"
    )
    
    # Dates
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = Field(None, description="Subscription end date")
    renewal_date: Optional[datetime] = Field(None, description="Next renewal date")
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation date")
    
    # Usage tracking
    content_accessed_count: int = Field(0, ge=0, description="Content pieces accessed this period")
    last_access_date: Optional[datetime] = Field(None, description="Last content access date")
    
    # Payment
    payment_method: Optional[str] = Field(None, description="Payment method identifier")
    auto_renew: bool = Field(True, description="Auto-renewal enabled")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    def is_active(self) -> bool:
        """Check if subscription is currently active."""
        if self.status != "active":
            return False
        
        if self.end_date and datetime.utcnow() > self.end_date:
            return False
        
        return True
    
    def has_access_to_level(self, access_level: AccessLevel) -> bool:
        """Check if subscription tier has access to content level."""
        tier_access_map = {
            SubscriptionTier.FREE: [AccessLevel.PUBLIC],
            SubscriptionTier.PREMIUM: [AccessLevel.PUBLIC, AccessLevel.REGISTERED, AccessLevel.PREMIUM],
            SubscriptionTier.ENTERPRISE: [
                AccessLevel.PUBLIC, AccessLevel.REGISTERED, 
                AccessLevel.PREMIUM, AccessLevel.ENTERPRISE
            ]
        }
        
        allowed_levels = tier_access_map.get(self.subscription_tier, [])
        return access_level in allowed_levels
    
    def can_access_more_content(self, plan: SubscriptionPlan) -> bool:
        """Check if user can access more content based on plan limits."""
        if plan.content_limit is None:
            return True
        
        return self.content_accessed_count < plan.content_limit


class AccessToken(BaseModel):
    """Time-limited access token for content."""
    
    token: str = Field(default_factory=lambda: secrets.token_urlsafe(32), description="Access token")
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    
    # Access details
    access_level: AccessLevel = Field(..., description="Granted access level")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Token expiration time")
    
    # Usage tracking
    used: bool = Field(False, description="Whether token has been used")
    used_at: Optional[datetime] = Field(None, description="Token usage timestamp")
    usage_count: int = Field(0, ge=0, description="Number of times token was used")
    max_uses: Optional[int] = Field(None, ge=1, description="Maximum allowed uses")
    
    # Payment tracking
    payment_token: Optional[str] = Field(None, description="Associated payment token")
    amount_paid: Optional[float] = Field(None, ge=0, description="Amount paid for access")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    def is_valid(self) -> bool:
        """Check if token is currently valid."""
        if datetime.utcnow() > self.expires_at:
            return False
        
        if self.max_uses is not None and self.usage_count >= self.max_uses:
            return False
        
        return True
    
    def mark_used(self):
        """Mark token as used."""
        self.used = True
        self.used_at = datetime.utcnow()
        self.usage_count += 1


class ContentValueAssessment(BaseModel):
    """Content value assessment for pricing and access control."""
    
    content_id: str = Field(..., description="Content identifier")
    
    # Value metrics
    value_tier: ContentValueTier = Field(..., description="Content value classification")
    quality_score: float = Field(..., ge=0.0, le=10.0, description="Content quality score")
    demand_score: float = Field(..., ge=0.0, le=10.0, description="Predicted demand score")
    exclusivity_score: float = Field(..., ge=0.0, le=10.0, description="Content exclusivity score")
    
    # Content characteristics
    freshness_days: int = Field(..., ge=0, description="Days since publication")
    word_count: int = Field(..., ge=0, description="Content word count")
    has_multimedia: bool = Field(False, description="Contains multimedia elements")
    is_investigative: bool = Field(False, description="Investigative journalism")
    is_breaking_news: bool = Field(False, description="Breaking news content")
    
    # Engagement predictions
    predicted_views: int = Field(0, ge=0, description="Predicted view count")
    predicted_shares: int = Field(0, ge=0, description="Predicted share count")
    predicted_engagement_rate: float = Field(0.0, ge=0.0, le=1.0, description="Predicted engagement rate")
    
    # Access recommendation
    recommended_access_level: AccessLevel = Field(..., description="Recommended access level")
    recommended_price: Optional[float] = Field(None, ge=0, description="Recommended price for pay-per-view")
    
    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    assessment_version: str = Field("1.0", description="Assessment algorithm version")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    def calculate_overall_value_score(self) -> float:
        """Calculate overall content value score (0-10)."""
        weights = {
            'quality': 0.30,
            'demand': 0.25,
            'exclusivity': 0.20,
            'freshness': 0.15,
            'engagement': 0.10
        }
        
        # Freshness score (newer is better, decays over 30 days)
        freshness_score = max(0, 10 - (self.freshness_days / 3))
        
        # Engagement score
        engagement_score = self.predicted_engagement_rate * 10
        
        overall_score = (
            self.quality_score * weights['quality'] +
            self.demand_score * weights['demand'] +
            self.exclusivity_score * weights['exclusivity'] +
            freshness_score * weights['freshness'] +
            engagement_score * weights['engagement']
        )
        
        return round(overall_score, 2)


class AccessVerificationRequest(BaseModel):
    """Request to verify content access rights."""
    
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    requested_access_level: AccessLevel = Field(..., description="Requested access level")
    
    # Optional authentication
    access_token: Optional[str] = Field(None, description="Access token if available")
    subscription_id: Optional[str] = Field(None, description="Subscription identifier")
    
    # Request context
    requesting_interface: str = Field(..., description="Interface making request")
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class AccessVerificationResponse(BaseModel):
    """Response to access verification request."""
    
    access_granted: bool = Field(..., description="Whether access is granted")
    access_level: AccessLevel = Field(..., description="Granted access level")
    
    # Denial information
    denial_reason: Optional[str] = Field(None, description="Reason for access denial")
    upgrade_required: bool = Field(False, description="Whether subscription upgrade is needed")
    
    # Access details
    access_token: Optional[str] = Field(None, description="Generated access token")
    expires_at: Optional[datetime] = Field(None, description="Access expiration time")
    
    # Subscription info
    current_subscription_tier: Optional[SubscriptionTier] = Field(None, description="User's current tier")
    required_subscription_tier: Optional[SubscriptionTier] = Field(None, description="Required tier for access")
    
    # Payment options
    pay_per_view_available: bool = Field(False, description="Pay-per-view option available")
    pay_per_view_price: Optional[float] = Field(None, ge=0, description="Pay-per-view price")
    
    # Metadata
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class TemporaryAccessGrant(BaseModel):
    """Temporary access grant for premium content."""
    
    grant_id: str = Field(default_factory=lambda: secrets.token_urlsafe(16), description="Grant identifier")
    user_id: str = Field(..., description="User identifier")
    content_id: str = Field(..., description="Content identifier")
    
    # Access details
    access_level: AccessLevel = Field(..., description="Granted access level")
    duration_seconds: int = Field(..., ge=1, description="Access duration in seconds")
    
    # Payment
    payment_token: str = Field(..., description="Payment verification token")
    amount_paid: float = Field(..., ge=0, description="Amount paid")
    payment_verified: bool = Field(False, description="Payment verification status")
    
    # Timestamps
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Access expiration time")
    
    # Usage
    accessed: bool = Field(False, description="Whether content was accessed")
    access_count: int = Field(0, ge=0, description="Number of accesses")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    @classmethod
    def create_grant(
        cls,
        user_id: str,
        content_id: str,
        access_level: AccessLevel,
        duration_seconds: int,
        payment_token: str,
        amount_paid: float
    ) -> "TemporaryAccessGrant":
        """Create a new temporary access grant."""
        granted_at = datetime.utcnow()
        expires_at = granted_at + timedelta(seconds=duration_seconds)
        
        return cls(
            user_id=user_id,
            content_id=content_id,
            access_level=access_level,
            duration_seconds=duration_seconds,
            payment_token=payment_token,
            amount_paid=amount_paid,
            granted_at=granted_at,
            expires_at=expires_at
        )
    
    def is_valid(self) -> bool:
        """Check if grant is currently valid."""
        return datetime.utcnow() < self.expires_at and self.payment_verified
