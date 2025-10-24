"""
Content-related MCP tools for brand-embedded content delivery.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

try:
    # Try relative imports first (for when running as module)
    from ...schemas.mcp_tools import (
        GetBrandedContentInput,
        GetBrandedContentOutput,
        CheckContentAccessInput,
        CheckContentAccessOutput,
        GrantTemporaryAccessInput,
        GrantTemporaryAccessOutput
    )
    from ...models.content import Article, BrandedContentResponse, ContentAccessRequest
    from ...models.brand import BrandMetadata, ComplianceTracking
    from ...models.access_control import AccessLevel, AccessVerificationRequest
    from ...services.access_control_manager import AccessControlManager
except ImportError:
    # Fall back to direct imports (for standalone execution)
    from schemas.mcp_tools import (
        GetBrandedContentInput,
        GetBrandedContentOutput,
        CheckContentAccessInput,
        CheckContentAccessOutput,
        GrantTemporaryAccessInput,
        GrantTemporaryAccessOutput
    )
    from models.content import Article, BrandedContentResponse, ContentAccessRequest
    from models.brand import BrandMetadata, ComplianceTracking
    from models.access_control import AccessLevel, AccessVerificationRequest
    from services.access_control_manager import AccessControlManager

logger = logging.getLogger(__name__)


class ContentTools:
    """Tools for content access and brand-embedded content delivery."""
    
    def __init__(self):
        """Initialize content tools with sample data."""
        self._sample_content = self._create_sample_content()
        self._access_tokens = {}  # In-memory storage for demo
        self._access_manager = AccessControlManager()  # Access control manager
        
    def _create_sample_content(self) -> Dict[str, Article]:
        """Create sample content for demonstration."""
        # This would typically come from a database
        # For now, creating minimal sample data structure
        return {
            "guardian-climate-2024": {
                "content_id": "guardian-climate-2024",
                "title": "Climate Change Report Reveals Shocking Trends",
                "text": "Recent climate data shows accelerating changes...",
                "summary": "New climate research reveals concerning trends in global temperature rise.",
                "brand_metadata": {
                    "publisher": {
                        "name": "The Guardian",
                        "trust_score": 9.2,
                        "established_year": 1821
                    }
                }
            }
        }
    
    async def get_branded_content(self, input_data: GetBrandedContentInput) -> GetBrandedContentOutput:
        """
        Retrieve content with full brand metadata and attribution requirements.
        
        This is the core MCP tool that delivers brand-embedded content to AI interfaces.
        """
        try:
            logger.info(f"Getting branded content for ID: {input_data.content_id}")
            
            # Check if content exists
            if input_data.content_id not in self._sample_content:
                return GetBrandedContentOutput(
                    success=False,
                    error_message=f"Content not found: {input_data.content_id}",
                    access_level="none"
                )
            
            # Get content data
            content_data = self._sample_content[input_data.content_id]
            
            # Check user access if user_id provided
            access_level = "free"  # Default access level
            if input_data.user_id:
                # In a real implementation, this would check user subscription
                access_level = self._check_user_access_level(input_data.user_id)
            
            # Create branded content response
            branded_content = {
                "content": content_data,
                "brand_package": content_data["brand_metadata"],
                "compliance_tracking": {
                    "tracking_id": f"track_{input_data.content_id}_{datetime.utcnow().timestamp()}",
                    "required_metrics": ["visibility_duration", "attribution_display", "user_engagement"],
                    "reporting_endpoint": "https://api.content-mcp.com/compliance/report"
                },
                "display_elements": self._generate_display_elements(
                    input_data.requesting_interface,
                    input_data.display_capabilities,
                    content_data["brand_metadata"]
                ),
                "interaction_options": self._generate_interaction_options(
                    input_data.requesting_interface,
                    access_level
                ),
                "access_level": access_level
            }
            
            logger.info(f"Successfully retrieved branded content for {input_data.content_id}")
            
            return GetBrandedContentOutput(
                success=True,
                content=branded_content,
                access_level=access_level
            )
            
        except Exception as e:
            logger.error(f"Error getting branded content: {str(e)}", exc_info=True)
            return GetBrandedContentOutput(
                success=False,
                error_message=f"Internal error: {str(e)}",
                access_level="none"
            )
    
    async def check_content_access(self, input_data: CheckContentAccessInput) -> CheckContentAccessOutput:
        """
        Verify user access rights for specific content.
        """
        try:
            logger.info(f"Checking access for user {input_data.user_id} to content {input_data.content_id}")
            
            # Check if content exists
            if input_data.content_id not in self._sample_content:
                return CheckContentAccessOutput(
                    access_granted=False,
                    access_level="none",
                    reason="Content not found"
                )
            
            # Parse access level
            try:
                requested_level = AccessLevel(input_data.access_level.lower())
            except ValueError:
                return CheckContentAccessOutput(
                    access_granted=False,
                    access_level="none",
                    reason=f"Invalid access level: {input_data.access_level}"
                )
            
            # Create verification request
            request = AccessVerificationRequest(
                user_id=input_data.user_id,
                content_id=input_data.content_id,
                requested_access_level=requested_level,
                requesting_interface=input_data.requesting_interface or "unknown"
            )
            
            # Verify access using AccessControlManager
            response = self._access_manager.verify_content_access(request)
            
            result = CheckContentAccessOutput(
                access_granted=response.access_granted,
                access_level=response.access_level.value,
                reason="Access granted" if response.access_granted else response.denial_reason
            )
            
            if response.access_granted:
                result.access_token = response.access_token
                result.expires_at = response.expires_at.isoformat() if response.expires_at else None
            else:
                # Add upgrade information
                if response.upgrade_required:
                    result.upgrade_required = True
                    result.current_tier = response.current_subscription_tier.value if response.current_subscription_tier else None
                    result.required_tier = response.required_subscription_tier.value if response.required_subscription_tier else None
                
                # Add pay-per-view information
                if response.pay_per_view_available:
                    result.pay_per_view_price = response.pay_per_view_price
            
            logger.info(f"Access check result: {response.access_granted} for user {input_data.user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error checking content access: {str(e)}", exc_info=True)
            return CheckContentAccessOutput(
                access_granted=False,
                access_level="none",
                reason=f"Error checking access: {str(e)}"
            )
    
    async def grant_temporary_access(self, input_data: GrantTemporaryAccessInput) -> GrantTemporaryAccessOutput:
        """
        Provide time-limited access to premium content.
        """
        try:
            logger.info(f"Granting temporary access for user {input_data.user_id} to content {input_data.content_id}")
            
            # Check if content exists
            if input_data.content_id not in self._sample_content:
                return GrantTemporaryAccessOutput(
                    access_granted=False,
                    error_message="Content not found"
                )
            
            # Validate payment token
            if not input_data.payment_token:
                return GrantTemporaryAccessOutput(
                    access_granted=False,
                    error_message="Payment token is required"
                )
            
            # Calculate amount paid (in real implementation, this would come from payment processor)
            amount_paid = 2.99  # Default pay-per-view price
            
            # Grant temporary access using AccessControlManager
            grant, message = self._access_manager.grant_temporary_access(
                user_id=input_data.user_id,
                content_id=input_data.content_id,
                duration_seconds=input_data.duration,
                payment_token=input_data.payment_token,
                amount_paid=amount_paid
            )
            
            if not grant:
                return GrantTemporaryAccessOutput(
                    access_granted=False,
                    error_message=message
                )
            
            logger.info(f"Temporary access granted: {grant.grant_id}")
            
            return GrantTemporaryAccessOutput(
                access_granted=True,
                access_token=grant.grant_id,
                expires_at=grant.expires_at.isoformat(),
                access_level=grant.access_level.value,
                amount_paid=grant.amount_paid
            )
            
        except Exception as e:
            logger.error(f"Error granting temporary access: {str(e)}", exc_info=True)
            return GrantTemporaryAccessOutput(
                access_granted=False,
                error_message=f"Error granting access: {str(e)}"
            )
    
    def _check_user_access_level(self, user_id: str) -> str:
        """Check user's subscription level (simplified for demo)."""
        # In a real implementation, this would query user database
        if user_id.startswith("premium_"):
            return "premium"
        elif user_id.startswith("enterprise_"):
            return "enterprise"
        else:
            return "free"
    
    def _is_access_granted(self, user_level: str, requested_level: str) -> bool:
        """Determine if user access level meets requested level."""
        access_hierarchy = {"free": 0, "premium": 1, "enterprise": 2}
        return access_hierarchy.get(user_level, 0) >= access_hierarchy.get(requested_level, 0)
    
    def _validate_payment_token(self, payment_token: str) -> bool:
        """Validate payment token (simplified for demo)."""
        # In a real implementation, this would validate with payment processor
        return payment_token.startswith("pay_") and len(payment_token) > 10
    
    def _generate_display_elements(self, interface: str, capabilities: Dict[str, bool], brand_metadata: Dict[str, Any]) -> list:
        """Generate interface-specific display elements."""
        elements = []
        
        if capabilities.get("supports_badges", False):
            elements.append({
                "type": "badge",
                "content": f"📰 {brand_metadata['publisher']['name']}",
                "style": "prominent"
            })
        
        if capabilities.get("supports_rich_formatting", False):
            elements.append({
                "type": "attribution_box",
                "content": f"✅ Fact-Checked | 🏆 Award-Winning | Est. {brand_metadata['publisher']['established_year']}",
                "style": "formatted"
            })
        
        return elements
    
    def _generate_interaction_options(self, interface: str, access_level: str) -> list:
        """Generate available user interaction options."""
        options = [
            {"type": "read_full_article", "label": "Read full article", "enabled": access_level != "free"}
        ]
        
        if access_level == "free":
            options.append({
                "type": "subscribe", 
                "label": "Subscribe for full access",
                "enabled": True
            })
        
        return options