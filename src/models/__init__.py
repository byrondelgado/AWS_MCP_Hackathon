"""
Core data models for the content publishing MCP server.

This package contains Pydantic models for brand metadata, content structure,
and validation utilities for publishing industry standards.
"""

from .brand import (
    PublisherMetadata,
    AttributionRequirements,
    EditorialMetadata,
    RightsMetadata,
    ContentCuration,
    DisplayRequirements,
    BrandMetadata,
    ComplianceTracking
)

from .content import (
    ContentType,
    ContentStatus,
    Author,
    ContentMetrics,
    Article,
    Publisher,
    BrandedContentResponse,
    ContentAccessRequest
)

from .validation import (
    ValidationResult,
    ISBNValidator,
    BrandMetadataValidator,
    ContentValidator,
    validate_content_quality,
    validate_metadata_completeness
)

from .access_control import (
    SubscriptionTier,
    AccessLevel,
    ContentValueTier,
    SubscriptionPlan,
    UserSubscription,
    AccessToken,
    ContentValueAssessment,
    AccessVerificationRequest,
    AccessVerificationResponse,
    TemporaryAccessGrant
)

__all__ = [
    # Brand models
    "PublisherMetadata",
    "AttributionRequirements", 
    "EditorialMetadata",
    "RightsMetadata",
    "ContentCuration",
    "DisplayRequirements",
    "BrandMetadata",
    "ComplianceTracking",
    
    # Content models
    "ContentType",
    "ContentStatus",
    "Author",
    "ContentMetrics",
    "Article",
    "Publisher",
    "BrandedContentResponse",
    "ContentAccessRequest",
    
    # Access control models
    "SubscriptionTier",
    "AccessLevel",
    "ContentValueTier",
    "SubscriptionPlan",
    "UserSubscription",
    "AccessToken",
    "ContentValueAssessment",
    "AccessVerificationRequest",
    "AccessVerificationResponse",
    "TemporaryAccessGrant",
    
    # Validation
    "ValidationResult",
    "ISBNValidator",
    "BrandMetadataValidator",
    "ContentValidator",
    "validate_content_quality",
    "validate_metadata_completeness"
]