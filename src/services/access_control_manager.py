"""
Access control management service for content gating and subscription management.

This service handles content access verification, subscription tier management,
access token generation/validation, and content value assessment.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import secrets

try:
    from ..models.access_control import (
        SubscriptionTier, AccessLevel, ContentValueTier,
        SubscriptionPlan, UserSubscription, AccessToken,
        ContentValueAssessment, AccessVerificationRequest,
        AccessVerificationResponse, TemporaryAccessGrant
    )
    from ..models.content import Article, ContentType
    from ..mcp_server.config import get_config
except ImportError:
    from models.access_control import (
        SubscriptionTier, AccessLevel, ContentValueTier,
        SubscriptionPlan, UserSubscription, AccessToken,
        ContentValueAssessment, AccessVerificationRequest,
        AccessVerificationResponse, TemporaryAccessGrant
    )
    from models.content import Article, ContentType
    from mcp_server.config import get_config

logger = logging.getLogger(__name__)


class AccessControlManager:
    """Manages content access control, subscriptions, and gating."""
    
    def __init__(self):
        """Initialize access control manager."""
        self.config = get_config()
        
        # In-memory storage for demo
        self._subscription_plans: Dict[str, SubscriptionPlan] = {}
        self._user_subscriptions: Dict[str, UserSubscription] = {}
        self._access_tokens: Dict[str, AccessToken] = {}
        self._content_assessments: Dict[str, ContentValueAssessment] = {}
        self._temporary_grants: Dict[str, TemporaryAccessGrant] = {}
        
        # Initialize default subscription plans
        self._initialize_subscription_plans()
    
    def _initialize_subscription_plans(self):
        """Initialize default subscription plans."""
        plans = [
            SubscriptionPlan(
                tier=SubscriptionTier.FREE,
                name="Free",
                description="Access to public content",
                price_monthly=0.0,
                price_annual=0.0,
                allowed_access_levels=[AccessLevel.PUBLIC],
                content_limit=10,
                features=[
                    "Access to public articles",
                    "Limited to 10 articles per month",
                    "Basic content only"
                ],
                priority_support=False,
                api_access=False
            ),
            SubscriptionPlan(
                tier=SubscriptionTier.PREMIUM,
                name="Premium",
                description="Full access to premium content",
                price_monthly=9.99,
                price_annual=99.99,
                allowed_access_levels=[
                    AccessLevel.PUBLIC,
                    AccessLevel.REGISTERED,
                    AccessLevel.PREMIUM
                ],
                content_limit=None,  # Unlimited
                features=[
                    "Unlimited access to all premium content",
                    "Ad-free experience",
                    "Early access to new content",
                    "Newsletter subscription",
                    "Mobile app access"
                ],
                priority_support=False,
                api_access=False
            ),
            SubscriptionPlan(
                tier=SubscriptionTier.ENTERPRISE,
                name="Enterprise",
                description="Enterprise-grade access with API",
                price_monthly=99.99,
                price_annual=999.99,
                allowed_access_levels=[
                    AccessLevel.PUBLIC,
                    AccessLevel.REGISTERED,
                    AccessLevel.PREMIUM,
                    AccessLevel.ENTERPRISE
                ],
                content_limit=None,  # Unlimited
                features=[
                    "All Premium features",
                    "API access for integration",
                    "Priority customer support",
                    "Custom content feeds",
                    "Analytics dashboard",
                    "White-label options",
                    "Dedicated account manager"
                ],
                priority_support=True,
                api_access=True
            )
        ]
        
        for plan in plans:
            plan_id = f"plan_{plan.tier.value}"
            self._subscription_plans[plan_id] = plan
        
        logger.info(f"Initialized {len(plans)} subscription plans")
    
    def get_subscription_plan(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID."""
        return self._subscription_plans.get(plan_id)
    
    def list_subscription_plans(self, active_only: bool = True) -> List[SubscriptionPlan]:
        """List all subscription plans."""
        plans = list(self._subscription_plans.values())
        if active_only:
            plans = [p for p in plans if p.is_active]
        return plans
    
    def get_user_subscription(self, user_id: str) -> Optional[UserSubscription]:
        """Get user's current subscription."""
        return self._user_subscriptions.get(user_id)
    
    def create_subscription(
        self,
        user_id: str,
        plan_id: str,
        payment_method: Optional[str] = None
    ) -> Tuple[Optional[UserSubscription], str]:
        """
        Create a new subscription for a user.
        
        Returns:
            Tuple of (UserSubscription or None, error message or success message)
        """
        plan = self._subscription_plans.get(plan_id)
        if not plan:
            return None, f"Subscription plan not found: {plan_id}"
        
        # Check if user already has an active subscription
        existing_sub = self._user_subscriptions.get(user_id)
        if existing_sub and existing_sub.is_active():
            return None, f"User already has an active subscription: {existing_sub.subscription_tier.value}"
        
        # Create subscription
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)  # Monthly by default
        renewal_date = end_date
        
        subscription = UserSubscription(
            user_id=user_id,
            subscription_tier=plan.tier,
            plan_id=plan_id,
            status="active",
            start_date=start_date,
            end_date=end_date,
            renewal_date=renewal_date,
            payment_method=payment_method,
            auto_renew=True
        )
        
        self._user_subscriptions[user_id] = subscription
        
        logger.info(f"Created {plan.tier.value} subscription for user {user_id}")
        return subscription, f"Successfully subscribed to {plan.name}"
    
    def cancel_subscription(self, user_id: str) -> Tuple[bool, str]:
        """
        Cancel a user's subscription.
        
        Returns:
            Tuple of (success boolean, message)
        """
        subscription = self._user_subscriptions.get(user_id)
        if not subscription:
            return False, "No subscription found for user"
        
        if subscription.status == "cancelled":
            return False, "Subscription is already cancelled"
        
        subscription.status = "cancelled"
        subscription.cancelled_at = datetime.utcnow()
        subscription.auto_renew = False
        subscription.updated_at = datetime.utcnow()
        
        logger.info(f"Cancelled subscription for user {user_id}")
        return True, "Subscription cancelled successfully"
    
    def verify_content_access(
        self,
        request: AccessVerificationRequest
    ) -> AccessVerificationResponse:
        """
        Verify if a user has access to specific content.
        
        Args:
            request: Access verification request
            
        Returns:
            AccessVerificationResponse with access decision
        """
        user_id = request.user_id
        content_id = request.content_id
        requested_level = request.requested_access_level
        
        # Check if access token is provided and valid
        if request.access_token:
            token = self._access_tokens.get(request.access_token)
            if token and token.is_valid() and token.content_id == content_id:
                token.mark_used()
                return AccessVerificationResponse(
                    access_granted=True,
                    access_level=token.access_level,
                    access_token=request.access_token,
                    expires_at=token.expires_at,
                    current_subscription_tier=None
                )
        
        # Get user subscription
        subscription = self._user_subscriptions.get(user_id)
        
        # If no subscription, treat as free tier
        if not subscription:
            subscription = UserSubscription(
                user_id=user_id,
                subscription_tier=SubscriptionTier.FREE,
                plan_id="plan_free",
                status="active"
            )
            self._user_subscriptions[user_id] = subscription
        
        # Check if subscription is active
        if not subscription.is_active():
            return AccessVerificationResponse(
                access_granted=False,
                access_level=AccessLevel.PUBLIC,
                denial_reason="Subscription is not active",
                upgrade_required=True,
                current_subscription_tier=subscription.subscription_tier,
                required_subscription_tier=self._get_required_tier_for_level(requested_level),
                pay_per_view_available=True,
                pay_per_view_price=self._calculate_pay_per_view_price(content_id)
            )
        
        # Check if subscription tier has access to requested level
        if not subscription.has_access_to_level(requested_level):
            return AccessVerificationResponse(
                access_granted=False,
                access_level=AccessLevel.PUBLIC,
                denial_reason=f"Subscription tier {subscription.subscription_tier.value} does not have access to {requested_level.value} content",
                upgrade_required=True,
                current_subscription_tier=subscription.subscription_tier,
                required_subscription_tier=self._get_required_tier_for_level(requested_level),
                pay_per_view_available=True,
                pay_per_view_price=self._calculate_pay_per_view_price(content_id)
            )
        
        # Check content limits
        plan = self._subscription_plans.get(subscription.plan_id)
        if plan and not subscription.can_access_more_content(plan):
            return AccessVerificationResponse(
                access_granted=False,
                access_level=AccessLevel.PUBLIC,
                denial_reason=f"Monthly content limit reached ({plan.content_limit} articles)",
                upgrade_required=True,
                current_subscription_tier=subscription.subscription_tier,
                required_subscription_tier=SubscriptionTier.PREMIUM,
                pay_per_view_available=True,
                pay_per_view_price=self._calculate_pay_per_view_price(content_id)
            )
        
        # Grant access
        subscription.content_accessed_count += 1
        subscription.last_access_date = datetime.utcnow()
        subscription.updated_at = datetime.utcnow()
        
        # Generate access token
        access_token = self._generate_access_token(
            user_id=user_id,
            content_id=content_id,
            access_level=requested_level,
            duration_hours=24
        )
        
        logger.info(f"Granted {requested_level.value} access to user {user_id} for content {content_id}")
        
        return AccessVerificationResponse(
            access_granted=True,
            access_level=requested_level,
            access_token=access_token.token,
            expires_at=access_token.expires_at,
            current_subscription_tier=subscription.subscription_tier
        )
    
    def grant_temporary_access(
        self,
        user_id: str,
        content_id: str,
        duration_seconds: int,
        payment_token: str,
        amount_paid: float
    ) -> Tuple[Optional[TemporaryAccessGrant], str]:
        """
        Grant temporary access to premium content (pay-per-view).
        
        Returns:
            Tuple of (TemporaryAccessGrant or None, message)
        """
        # Verify payment token (in production, this would verify with payment processor)
        if not payment_token or len(payment_token) < 10:
            return None, "Invalid payment token"
        
        # Get content assessment to determine access level
        assessment = self._content_assessments.get(content_id)
        if not assessment:
            # Default to premium access
            access_level = AccessLevel.PREMIUM
        else:
            access_level = assessment.recommended_access_level
        
        # Create temporary grant
        grant = TemporaryAccessGrant.create_grant(
            user_id=user_id,
            content_id=content_id,
            access_level=access_level,
            duration_seconds=duration_seconds,
            payment_token=payment_token,
            amount_paid=amount_paid
        )
        
        # Verify payment (simplified for demo)
        grant.payment_verified = True
        
        # Store grant
        self._temporary_grants[grant.grant_id] = grant
        
        # Generate access token
        access_token = self._generate_access_token(
            user_id=user_id,
            content_id=content_id,
            access_level=access_level,
            duration_hours=duration_seconds / 3600,
            payment_token=payment_token,
            amount_paid=amount_paid
        )
        
        logger.info(f"Granted temporary {access_level.value} access to user {user_id} for content {content_id}")
        
        return grant, f"Temporary access granted for {duration_seconds} seconds"
    
    def assess_content_value(
        self,
        article: Article,
        publisher_trust_score: float = 7.0
    ) -> ContentValueAssessment:
        """
        Assess content value for pricing and access control decisions.
        
        Args:
            article: Article to assess
            publisher_trust_score: Publisher's trust score
            
        Returns:
            ContentValueAssessment with recommendations
        """
        # Calculate quality score based on multiple factors
        quality_factors = []
        
        # Publisher trust score contributes to quality
        quality_factors.append(publisher_trust_score)
        
        # Fact-checked content gets bonus
        if article.brand_metadata.editorial.fact_checked:
            quality_factors.append(9.0)
        else:
            quality_factors.append(6.0)
        
        # Verification level affects quality
        verification_scores = {
            "triple-sourced": 9.5,
            "peer-reviewed": 9.0,
            "double-sourced": 7.5,
            "single-sourced": 6.0
        }
        verification_level = article.brand_metadata.editorial.verification_level
        quality_factors.append(verification_scores.get(verification_level, 6.0))
        
        quality_score = sum(quality_factors) / len(quality_factors)
        
        # Calculate demand score based on content type and characteristics
        demand_score = 5.0  # Base demand
        
        if article.content_type == ContentType.BREAKING_NEWS:
            demand_score += 3.0
        elif article.content_type == ContentType.FEATURE:
            demand_score += 2.0
        elif article.content_type == ContentType.OPINION:
            demand_score += 1.0
        
        # Adjust for metrics if available
        if article.metrics:
            engagement_factor = min(article.metrics.engagement_score / 5.0, 2.0)
            demand_score += engagement_factor
        
        demand_score = min(demand_score, 10.0)
        
        # Calculate exclusivity score
        exclusivity_score = 5.0  # Base exclusivity
        
        # Investigative journalism is more exclusive
        if article.content_type in [ContentType.FEATURE, ContentType.INTERVIEW]:
            exclusivity_score += 2.0
        
        # High trust publishers have more exclusive content
        if publisher_trust_score >= 9.0:
            exclusivity_score += 2.0
        elif publisher_trust_score >= 8.0:
            exclusivity_score += 1.0
        
        exclusivity_score = min(exclusivity_score, 10.0)
        
        # Calculate freshness
        if article.publish_date:
            freshness_days = (datetime.utcnow() - article.publish_date).days
        else:
            freshness_days = 0
        
        # Get word count
        word_count = article.metrics.word_count if article.metrics and article.metrics.word_count else len(article.text.split())
        
        # Determine value tier
        overall_value = (quality_score + demand_score + exclusivity_score) / 3
        
        if overall_value >= 8.5:
            value_tier = ContentValueTier.EXCLUSIVE
            recommended_access_level = AccessLevel.ENTERPRISE
            recommended_price = 4.99
        elif overall_value >= 7.0:
            value_tier = ContentValueTier.PREMIUM
            recommended_access_level = AccessLevel.PREMIUM
            recommended_price = 2.99
        elif overall_value >= 5.5:
            value_tier = ContentValueTier.STANDARD
            recommended_access_level = AccessLevel.REGISTERED
            recommended_price = 0.99
        else:
            value_tier = ContentValueTier.BASIC
            recommended_access_level = AccessLevel.PUBLIC
            recommended_price = 0.0
        
        # Predict engagement
        predicted_engagement_rate = min((quality_score + demand_score) / 20.0, 0.95)
        predicted_views = int(1000 * (demand_score / 5.0) * (publisher_trust_score / 5.0))
        predicted_shares = int(predicted_views * predicted_engagement_rate * 0.1)
        
        assessment = ContentValueAssessment(
            content_id=article.content_id,
            value_tier=value_tier,
            quality_score=round(quality_score, 2),
            demand_score=round(demand_score, 2),
            exclusivity_score=round(exclusivity_score, 2),
            freshness_days=freshness_days,
            word_count=word_count,
            has_multimedia=False,  # Could be enhanced
            is_investigative=article.content_type == ContentType.FEATURE,
            is_breaking_news=article.content_type == ContentType.BREAKING_NEWS,
            predicted_views=predicted_views,
            predicted_shares=predicted_shares,
            predicted_engagement_rate=round(predicted_engagement_rate, 3),
            recommended_access_level=recommended_access_level,
            recommended_price=recommended_price
        )
        
        # Store assessment
        self._content_assessments[article.content_id] = assessment
        
        logger.info(f"Assessed content {article.content_id}: {value_tier.value} tier, {recommended_access_level.value} access")
        
        return assessment
    
    def _generate_access_token(
        self,
        user_id: str,
        content_id: str,
        access_level: AccessLevel,
        duration_hours: float = 24.0,
        payment_token: Optional[str] = None,
        amount_paid: Optional[float] = None
    ) -> AccessToken:
        """Generate a new access token."""
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        token = AccessToken(
            user_id=user_id,
            content_id=content_id,
            access_level=access_level,
            expires_at=expires_at,
            payment_token=payment_token,
            amount_paid=amount_paid
        )
        
        self._access_tokens[token.token] = token
        
        return token
    
    def validate_access_token(self, token_str: str) -> Tuple[bool, Optional[AccessToken], str]:
        """
        Validate an access token.
        
        Returns:
            Tuple of (is_valid, token or None, message)
        """
        token = self._access_tokens.get(token_str)
        
        if not token:
            return False, None, "Token not found"
        
        if not token.is_valid():
            if datetime.utcnow() > token.expires_at:
                return False, token, "Token has expired"
            elif token.max_uses and token.usage_count >= token.max_uses:
                return False, token, "Token usage limit exceeded"
            else:
                return False, token, "Token is invalid"
        
        return True, token, "Token is valid"
    
    def _get_required_tier_for_level(self, access_level: AccessLevel) -> SubscriptionTier:
        """Get the minimum subscription tier required for an access level."""
        level_tier_map = {
            AccessLevel.PUBLIC: SubscriptionTier.FREE,
            AccessLevel.REGISTERED: SubscriptionTier.PREMIUM,
            AccessLevel.PREMIUM: SubscriptionTier.PREMIUM,
            AccessLevel.ENTERPRISE: SubscriptionTier.ENTERPRISE,
            AccessLevel.RESTRICTED: SubscriptionTier.ENTERPRISE
        }
        
        return level_tier_map.get(access_level, SubscriptionTier.PREMIUM)
    
    def _calculate_pay_per_view_price(self, content_id: str) -> float:
        """Calculate pay-per-view price for content."""
        assessment = self._content_assessments.get(content_id)
        
        if assessment and assessment.recommended_price:
            return assessment.recommended_price
        
        # Default pricing
        return 1.99
    
    def get_access_statistics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get access control statistics."""
        if user_id:
            # User-specific statistics
            subscription = self._user_subscriptions.get(user_id)
            user_tokens = [t for t in self._access_tokens.values() if t.user_id == user_id]
            user_grants = [g for g in self._temporary_grants.values() if g.user_id == user_id]
            
            return {
                "user_id": user_id,
                "subscription": {
                    "tier": subscription.subscription_tier.value if subscription else "none",
                    "status": subscription.status if subscription else "none",
                    "content_accessed": subscription.content_accessed_count if subscription else 0,
                    "is_active": subscription.is_active() if subscription else False
                },
                "access_tokens": {
                    "total": len(user_tokens),
                    "valid": len([t for t in user_tokens if t.is_valid()]),
                    "expired": len([t for t in user_tokens if not t.is_valid()])
                },
                "temporary_grants": {
                    "total": len(user_grants),
                    "active": len([g for g in user_grants if g.is_valid()]),
                    "total_spent": sum(g.amount_paid for g in user_grants)
                }
            }
        else:
            # Global statistics
            active_subscriptions = [s for s in self._user_subscriptions.values() if s.is_active()]
            
            tier_distribution = {}
            for tier in SubscriptionTier:
                tier_distribution[tier.value] = len([s for s in active_subscriptions if s.subscription_tier == tier])
            
            return {
                "total_users": len(self._user_subscriptions),
                "active_subscriptions": len(active_subscriptions),
                "tier_distribution": tier_distribution,
                "total_access_tokens": len(self._access_tokens),
                "valid_tokens": len([t for t in self._access_tokens.values() if t.is_valid()]),
                "total_temporary_grants": len(self._temporary_grants),
                "active_grants": len([g for g in self._temporary_grants.values() if g.is_valid()]),
                "total_revenue": sum(g.amount_paid for g in self._temporary_grants.values()),
                "content_assessments": len(self._content_assessments)
            }
