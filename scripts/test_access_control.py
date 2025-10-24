#!/usr/bin/env python3
"""
Test script for content access control system.

This script demonstrates:
- Subscription tier management
- Content access verification
- Access token generation and validation
- Content value assessment
- Temporary access grants (pay-per-view)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.access_control_manager import AccessControlManager
from services.brand_manager import BrandManager
from models.access_control import (
    AccessLevel, SubscriptionTier, AccessVerificationRequest
)
from models.content import Article, ContentType, Author
from models.brand import BrandMetadata
import json


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_json(data: dict, indent: int = 2):
    """Print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


def main():
    """Run access control system tests."""
    print_section("Content Access Control System Test")
    
    # Initialize managers
    access_manager = AccessControlManager()
    brand_manager = BrandManager()
    
    # Test 1: List subscription plans
    print_section("1. Available Subscription Plans")
    plans = access_manager.list_subscription_plans()
    for plan in plans:
        print(f"\n{plan.name} ({plan.tier.value})")
        print(f"  Price: ${plan.price_monthly}/month")
        print(f"  Features: {', '.join(plan.features[:3])}...")
        print(f"  Access Levels: {[level.value for level in plan.allowed_access_levels]}")
        print(f"  Content Limit: {'Unlimited' if plan.content_limit is None else plan.content_limit}")
    
    # Test 2: Create subscriptions for test users
    print_section("2. Creating Test User Subscriptions")
    
    test_users = [
        ("user_free_001", "free"),
        ("user_premium_001", "premium"),
        ("user_enterprise_001", "enterprise")
    ]
    
    for user_id, tier in test_users:
        subscription, message = access_manager.create_subscription(
            user_id=user_id,
            plan_id=f"plan_{tier}",
            payment_method="test_payment_method"
        )
        
        if subscription:
            print(f"✓ Created {tier} subscription for {user_id}")
            print(f"  Status: {subscription.status}")
            print(f"  Expires: {subscription.end_date}")
        else:
            print(f"✗ Failed to create subscription: {message}")
    
    # Test 3: Content access verification
    print_section("3. Content Access Verification")
    
    test_content_id = "article_001"
    access_tests = [
        ("user_free_001", AccessLevel.PUBLIC, "Free user accessing public content"),
        ("user_free_001", AccessLevel.PREMIUM, "Free user accessing premium content"),
        ("user_premium_001", AccessLevel.PREMIUM, "Premium user accessing premium content"),
        ("user_premium_001", AccessLevel.ENTERPRISE, "Premium user accessing enterprise content"),
        ("user_enterprise_001", AccessLevel.ENTERPRISE, "Enterprise user accessing enterprise content"),
    ]
    
    for user_id, access_level, description in access_tests:
        print(f"\nTest: {description}")
        
        request = AccessVerificationRequest(
            user_id=user_id,
            content_id=test_content_id,
            requested_access_level=access_level,
            requesting_interface="test_script"
        )
        
        response = access_manager.verify_content_access(request)
        
        if response.access_granted:
            print(f"  ✓ Access GRANTED")
            print(f"    Access Level: {response.access_level.value}")
            print(f"    Token: {response.access_token[:20]}...")
        else:
            print(f"  ✗ Access DENIED")
            print(f"    Reason: {response.denial_reason}")
            print(f"    Current Tier: {response.current_subscription_tier.value if response.current_subscription_tier else 'none'}")
            print(f"    Required Tier: {response.required_subscription_tier.value if response.required_subscription_tier else 'none'}")
            if response.pay_per_view_available:
                print(f"    Pay-per-view: ${response.pay_per_view_price}")
    
    # Test 4: Access token validation
    print_section("4. Access Token Validation")
    
    # Generate a token
    request = AccessVerificationRequest(
        user_id="user_premium_001",
        content_id=test_content_id,
        requested_access_level=AccessLevel.PREMIUM,
        requesting_interface="test_script"
    )
    response = access_manager.verify_content_access(request)
    
    if response.access_granted and response.access_token:
        print(f"Generated token: {response.access_token[:30]}...")
        
        # Validate the token
        is_valid, token, message = access_manager.validate_access_token(response.access_token)
        
        print(f"\nToken validation: {'✓ VALID' if is_valid else '✗ INVALID'}")
        print(f"  Message: {message}")
        if token:
            print(f"  User: {token.user_id}")
            print(f"  Content: {token.content_id}")
            print(f"  Access Level: {token.access_level.value}")
            print(f"  Expires: {token.expires_at}")
            print(f"  Usage Count: {token.usage_count}")
    
    # Test 5: Content value assessment
    print_section("5. Content Value Assessment")
    
    # Get Guardian publisher
    guardian = brand_manager.get_publisher("guardian")
    
    if guardian:
        # Create brand metadata for test article
        brand_metadata, _ = brand_manager.create_brand_metadata_package(
            publisher_id="guardian",
            content_type="article"
        )
        
        if brand_metadata:
            # Create test article
            test_article = Article(
                content_id="article_guardian_001",
                title="Climate Change Report Reveals Shocking Trends",
                text="A comprehensive investigation into climate change impacts...",
                summary="New research shows accelerating climate change effects",
                content_type=ContentType.FEATURE,
                authors=[
                    Author(
                        name="Jane Smith",
                        credentials=["Award-winning environmental reporter", "20 years experience"]
                    )
                ],
                brand_metadata=brand_metadata
            )
            
            # Assess content value
            assessment = access_manager.assess_content_value(
                article=test_article,
                publisher_trust_score=guardian.trust_score
            )
            
            print(f"Content: {test_article.title}")
            print(f"Publisher: {guardian.name} (Trust Score: {guardian.trust_score})")
            print(f"\nAssessment Results:")
            print(f"  Value Tier: {assessment.value_tier.value}")
            print(f"  Quality Score: {assessment.quality_score}/10")
            print(f"  Demand Score: {assessment.demand_score}/10")
            print(f"  Exclusivity Score: {assessment.exclusivity_score}/10")
            print(f"  Overall Value: {assessment.calculate_overall_value_score()}/10")
            print(f"\nRecommendations:")
            print(f"  Access Level: {assessment.recommended_access_level.value}")
            print(f"  Price: ${assessment.recommended_price}")
            print(f"\nPredictions:")
            print(f"  Views: {assessment.predicted_views:,}")
            print(f"  Shares: {assessment.predicted_shares:,}")
            print(f"  Engagement Rate: {assessment.predicted_engagement_rate:.1%}")
    
    # Test 6: Temporary access grants (pay-per-view)
    print_section("6. Temporary Access Grants (Pay-per-View)")
    
    grant, message = access_manager.grant_temporary_access(
        user_id="user_free_001",
        content_id="article_premium_001",
        duration_seconds=3600,  # 1 hour
        payment_token="test_payment_token_12345",
        amount_paid=2.99
    )
    
    if grant:
        print(f"✓ Temporary access granted")
        print(f"  Grant ID: {grant.grant_id}")
        print(f"  User: {grant.user_id}")
        print(f"  Content: {grant.content_id}")
        print(f"  Access Level: {grant.access_level.value}")
        print(f"  Duration: {grant.duration_seconds / 3600:.1f} hours")
        print(f"  Amount Paid: ${grant.amount_paid}")
        print(f"  Granted At: {grant.granted_at}")
        print(f"  Expires At: {grant.expires_at}")
        print(f"  Payment Verified: {grant.payment_verified}")
        print(f"  Is Valid: {grant.is_valid()}")
    else:
        print(f"✗ Failed to grant temporary access: {message}")
    
    # Test 7: Access statistics
    print_section("7. Access Control Statistics")
    
    # Global statistics
    global_stats = access_manager.get_access_statistics()
    print("Global Statistics:")
    print_json(global_stats)
    
    # User-specific statistics
    print("\nUser Statistics (user_premium_001):")
    user_stats = access_manager.get_access_statistics(user_id="user_premium_001")
    print_json(user_stats)
    
    # Test 8: Subscription cancellation
    print_section("8. Subscription Cancellation")
    
    success, message = access_manager.cancel_subscription("user_free_001")
    print(f"Cancel subscription for user_free_001: {'✓ SUCCESS' if success else '✗ FAILED'}")
    print(f"  Message: {message}")
    
    # Verify cancellation
    subscription = access_manager.get_user_subscription("user_free_001")
    if subscription:
        print(f"  Status: {subscription.status}")
        print(f"  Cancelled At: {subscription.cancelled_at}")
        print(f"  Auto Renew: {subscription.auto_renew}")
    
    print_section("Test Complete")
    print("All access control system tests completed successfully!\n")


if __name__ == "__main__":
    main()
