"""
MCP tools for content access control and subscription management.

These tools provide content gating, access verification, subscription management,
and temporary access grants for the MCP server.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from ...models.access_control import (
        AccessLevel, SubscriptionTier, AccessVerificationRequest
    )
    from ...services.access_control_manager import AccessControlManager
    from ...services.brand_manager import BrandManager
    from ...models.content import Article
except ImportError:
    from models.access_control import (
        AccessLevel, SubscriptionTier, AccessVerificationRequest
    )
    from services.access_control_manager import AccessControlManager
    from services.brand_manager import BrandManager
    from models.content import Article

logger = logging.getLogger(__name__)

# Global manager instances
access_manager = AccessControlManager()
brand_manager = BrandManager()


def check_content_access(
    user_id: str,
    content_id: str,
    access_level: str = "free",
    requesting_interface: str = "unknown",
    access_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify user access rights for specific content.
    
    Args:
        user_id: User identifier
        content_id: Content identifier
        access_level: Requested access level (public, registered, premium, enterprise)
        requesting_interface: AI interface making the request
        access_token: Optional access token for verification
        
    Returns:
        Dictionary with access verification results
    """
    try:
        # Parse access level
        try:
            requested_level = AccessLevel(access_level.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid access level: {access_level}. Must be one of: public, registered, premium, enterprise, restricted"
            }
        
        # Create verification request
        request = AccessVerificationRequest(
            user_id=user_id,
            content_id=content_id,
            requested_access_level=requested_level,
            requesting_interface=requesting_interface,
            access_token=access_token
        )
        
        # Verify access
        response = access_manager.verify_content_access(request)
        
        result = {
            "success": True,
            "access_granted": response.access_granted,
            "access_level": response.access_level.value,
            "user_id": user_id,
            "content_id": content_id
        }
        
        if response.access_granted:
            result.update({
                "access_token": response.access_token,
                "expires_at": response.expires_at.isoformat() if response.expires_at else None,
                "message": f"Access granted to {response.access_level.value} content"
            })
        else:
            result.update({
                "denial_reason": response.denial_reason,
                "upgrade_required": response.upgrade_required,
                "current_tier": response.current_subscription_tier.value if response.current_subscription_tier else "none",
                "required_tier": response.required_subscription_tier.value if response.required_subscription_tier else None,
                "pay_per_view_available": response.pay_per_view_available,
                "pay_per_view_price": response.pay_per_view_price
            })
        
        logger.info(f"Access check for user {user_id}, content {content_id}: {'granted' if response.access_granted else 'denied'}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking content access: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to check content access: {str(e)}"
        }


def grant_temporary_access(
    user_id: str,
    content_id: str,
    duration_hours: float = 24.0,
    payment_token: str = "",
    amount_paid: float = 0.0
) -> Dict[str, Any]:
    """
    Provide time-limited access to premium content (pay-per-view).
    
    Args:
        user_id: User identifier
        content_id: Content identifier
        duration_hours: Access duration in hours (default: 24)
        payment_token: Payment verification token
        amount_paid: Amount paid for access
        
    Returns:
        Dictionary with temporary access grant details
    """
    try:
        if not payment_token:
            return {
                "success": False,
                "error": "Payment token is required for temporary access"
            }
        
        if amount_paid <= 0:
            return {
                "success": False,
                "error": "Payment amount must be greater than 0"
            }
        
        duration_seconds = int(duration_hours * 3600)
        
        # Grant temporary access
        grant, message = access_manager.grant_temporary_access(
            user_id=user_id,
            content_id=content_id,
            duration_seconds=duration_seconds,
            payment_token=payment_token,
            amount_paid=amount_paid
        )
        
        if not grant:
            return {
                "success": False,
                "error": message
            }
        
        result = {
            "success": True,
            "grant_id": grant.grant_id,
            "user_id": user_id,
            "content_id": content_id,
            "access_level": grant.access_level.value,
            "duration_hours": duration_hours,
            "amount_paid": amount_paid,
            "granted_at": grant.granted_at.isoformat(),
            "expires_at": grant.expires_at.isoformat(),
            "payment_verified": grant.payment_verified,
            "message": message
        }
        
        logger.info(f"Granted temporary access to user {user_id} for content {content_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error granting temporary access: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to grant temporary access: {str(e)}"
        }


def get_subscription_plans() -> Dict[str, Any]:
    """
    Get available subscription plans.
    
    Returns:
        Dictionary with subscription plan details
    """
    try:
        plans = access_manager.list_subscription_plans(active_only=True)
        
        result = {
            "success": True,
            "plans": []
        }
        
        for plan in plans:
            plan_data = {
                "tier": plan.tier.value,
                "name": plan.name,
                "description": plan.description,
                "price_monthly": plan.price_monthly,
                "price_annual": plan.price_annual,
                "features": plan.features,
                "content_limit": plan.content_limit,
                "priority_support": plan.priority_support,
                "api_access": plan.api_access,
                "allowed_access_levels": [level.value for level in plan.allowed_access_levels]
            }
            result["plans"].append(plan_data)
        
        logger.info(f"Retrieved {len(plans)} subscription plans")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting subscription plans: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get subscription plans: {str(e)}"
        }


def create_subscription(
    user_id: str,
    tier: str = "premium",
    payment_method: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new subscription for a user.
    
    Args:
        user_id: User identifier
        tier: Subscription tier (free, premium, enterprise)
        payment_method: Payment method identifier
        
    Returns:
        Dictionary with subscription creation results
    """
    try:
        # Validate tier
        try:
            subscription_tier = SubscriptionTier(tier.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid subscription tier: {tier}. Must be one of: free, premium, enterprise"
            }
        
        plan_id = f"plan_{subscription_tier.value}"
        
        # Create subscription
        subscription, message = access_manager.create_subscription(
            user_id=user_id,
            plan_id=plan_id,
            payment_method=payment_method
        )
        
        if not subscription:
            return {
                "success": False,
                "error": message
            }
        
        result = {
            "success": True,
            "user_id": user_id,
            "subscription_tier": subscription.subscription_tier.value,
            "status": subscription.status,
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "renewal_date": subscription.renewal_date.isoformat() if subscription.renewal_date else None,
            "auto_renew": subscription.auto_renew,
            "message": message
        }
        
        logger.info(f"Created {subscription_tier.value} subscription for user {user_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to create subscription: {str(e)}"
        }


def get_user_subscription(user_id: str) -> Dict[str, Any]:
    """
    Get user's current subscription details.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with subscription details
    """
    try:
        subscription = access_manager.get_user_subscription(user_id)
        
        if not subscription:
            return {
                "success": True,
                "user_id": user_id,
                "has_subscription": False,
                "message": "No subscription found for user"
            }
        
        result = {
            "success": True,
            "user_id": user_id,
            "has_subscription": True,
            "subscription_tier": subscription.subscription_tier.value,
            "status": subscription.status,
            "is_active": subscription.is_active(),
            "start_date": subscription.start_date.isoformat(),
            "end_date": subscription.end_date.isoformat() if subscription.end_date else None,
            "renewal_date": subscription.renewal_date.isoformat() if subscription.renewal_date else None,
            "content_accessed_count": subscription.content_accessed_count,
            "last_access_date": subscription.last_access_date.isoformat() if subscription.last_access_date else None,
            "auto_renew": subscription.auto_renew
        }
        
        logger.info(f"Retrieved subscription for user {user_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user subscription: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get user subscription: {str(e)}"
        }


def cancel_subscription(user_id: str) -> Dict[str, Any]:
    """
    Cancel a user's subscription.
    
    Args:
        user_id: User identifier
        
    Returns:
        Dictionary with cancellation results
    """
    try:
        success, message = access_manager.cancel_subscription(user_id)
        
        result = {
            "success": success,
            "user_id": user_id,
            "message": message
        }
        
        if success:
            logger.info(f"Cancelled subscription for user {user_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to cancel subscription: {str(e)}"
        }


def assess_content_value(
    content_id: str,
    publisher_id: str
) -> Dict[str, Any]:
    """
    Assess content value for pricing and access control decisions.
    
    Args:
        content_id: Content identifier
        publisher_id: Publisher identifier
        
    Returns:
        Dictionary with content value assessment
    """
    try:
        # This is a simplified version - in production, you'd fetch the actual article
        # For now, we'll return a mock assessment
        publisher = brand_manager.get_publisher(publisher_id)
        if not publisher:
            return {
                "success": False,
                "error": f"Publisher not found: {publisher_id}"
            }
        
        # Create a mock assessment based on publisher trust score
        trust_score = publisher.trust_score
        
        # Determine value tier based on trust score
        if trust_score >= 9.0:
            value_tier = "exclusive"
            recommended_access = "enterprise"
            recommended_price = 4.99
            quality_score = 9.2
            demand_score = 8.5
            exclusivity_score = 9.0
        elif trust_score >= 8.0:
            value_tier = "premium"
            recommended_access = "premium"
            recommended_price = 2.99
            quality_score = 8.0
            demand_score = 7.5
            exclusivity_score = 7.5
        elif trust_score >= 7.0:
            value_tier = "standard"
            recommended_access = "registered"
            recommended_price = 0.99
            quality_score = 7.0
            demand_score = 6.5
            exclusivity_score = 6.0
        else:
            value_tier = "basic"
            recommended_access = "public"
            recommended_price = 0.0
            quality_score = 6.0
            demand_score = 5.5
            exclusivity_score = 5.0
        
        result = {
            "success": True,
            "content_id": content_id,
            "publisher_id": publisher_id,
            "value_tier": value_tier,
            "quality_score": quality_score,
            "demand_score": demand_score,
            "exclusivity_score": exclusivity_score,
            "overall_value_score": round((quality_score + demand_score + exclusivity_score) / 3, 2),
            "recommended_access_level": recommended_access,
            "recommended_price": recommended_price,
            "assessed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Assessed content {content_id}: {value_tier} tier")
        
        return result
        
    except Exception as e:
        logger.error(f"Error assessing content value: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to assess content value: {str(e)}"
        }


def get_access_statistics(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get access control and subscription statistics.
    
    Args:
        user_id: Optional user identifier for user-specific stats
        
    Returns:
        Dictionary with access statistics
    """
    try:
        stats = access_manager.get_access_statistics(user_id=user_id)
        
        result = {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Retrieved access statistics{' for user ' + user_id if user_id else ''}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting access statistics: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Failed to get access statistics: {str(e)}"
        }
