#!/usr/bin/env python3
"""
Test script for MCP access control tools integration.

This script tests the integration between MCP tools and the access control system.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.tools.content_tools import ContentTools
from schemas.mcp_tools import (
    CheckContentAccessInput,
    GrantTemporaryAccessInput
)
from services.access_control_manager import AccessControlManager
import json


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_json(data: dict, indent: int = 2):
    """Print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


async def main():
    """Run MCP access control tools tests."""
    print_section("MCP Access Control Tools Integration Test")
    
    # Initialize tools and manager
    content_tools = ContentTools()
    access_manager = content_tools._access_manager
    
    # Setup test users with subscriptions
    print_section("1. Setting Up Test Users")
    
    test_users = [
        ("user_free_mcp", "free"),
        ("user_premium_mcp", "premium"),
        ("user_enterprise_mcp", "enterprise")
    ]
    
    for user_id, tier in test_users:
        subscription, message = access_manager.create_subscription(
            user_id=user_id,
            plan_id=f"plan_{tier}",
            payment_method="test_payment"
        )
        
        if subscription:
            print(f"✓ Created {tier} subscription for {user_id}")
        else:
            print(f"✗ Failed: {message}")
    
    # Test 2: MCP check_content_access tool
    print_section("2. Testing check_content_access MCP Tool")
    
    access_tests = [
        ("user_free_mcp", "public", "Free user accessing public content"),
        ("user_free_mcp", "premium", "Free user accessing premium content (should be denied)"),
        ("user_premium_mcp", "premium", "Premium user accessing premium content"),
        ("user_premium_mcp", "enterprise", "Premium user accessing enterprise content (should be denied)"),
        ("user_enterprise_mcp", "enterprise", "Enterprise user accessing enterprise content"),
    ]
    
    for user_id, access_level, description in access_tests:
        print(f"\nTest: {description}")
        
        input_data = CheckContentAccessInput(
            user_id=user_id,
            content_id="guardian-climate-2024",
            access_level=access_level,
            requesting_interface="test_mcp_client"
        )
        
        result = await content_tools.check_content_access(input_data)
        
        print(f"  Access Granted: {result.access_granted}")
        print(f"  Access Level: {result.access_level}")
        print(f"  Reason: {result.reason}")
        
        if result.access_granted:
            print(f"  Token: {result.access_token[:30] if result.access_token else 'None'}...")
            print(f"  Expires: {result.expires_at}")
        else:
            if result.upgrade_required:
                print(f"  Upgrade Required: Yes")
                print(f"  Current Tier: {result.current_tier}")
                print(f"  Required Tier: {result.required_tier}")
            if result.pay_per_view_price:
                print(f"  Pay-per-view Price: ${result.pay_per_view_price}")
    
    # Test 3: MCP grant_temporary_access tool
    print_section("3. Testing grant_temporary_access MCP Tool")
    
    print("Test: Free user purchasing temporary access")
    
    input_data = GrantTemporaryAccessInput(
        user_id="user_free_mcp",
        content_id="guardian-climate-2024",
        duration=3600,  # 1 hour
        payment_token="pay_test_token_12345678"
    )
    
    result = await content_tools.grant_temporary_access(input_data)
    
    print(f"  Access Granted: {result.access_granted}")
    
    if result.access_granted:
        print(f"  Access Token: {result.access_token[:30]}...")
        print(f"  Access Level: {result.access_level}")
        print(f"  Amount Paid: ${result.amount_paid}")
        print(f"  Expires: {result.expires_at}")
    else:
        print(f"  Error: {result.error_message}")
    
    # Test 4: Verify temporary access works
    print_section("4. Verifying Temporary Access")
    
    if result.access_granted:
        print("Test: Using temporary access token")
        
        # Try to access content with the temporary token
        verify_input = CheckContentAccessInput(
            user_id="user_free_mcp",
            content_id="guardian-climate-2024",
            access_level="premium",
            requesting_interface="test_mcp_client"
        )
        
        verify_result = await content_tools.check_content_access(verify_input)
        
        print(f"  Access Granted: {verify_result.access_granted}")
        print(f"  Access Level: {verify_result.access_level}")
        print(f"  Reason: {verify_result.reason}")
    
    # Test 5: Access statistics
    print_section("5. Access Control Statistics")
    
    stats = access_manager.get_access_statistics()
    print("Global Statistics:")
    print_json(stats)
    
    print("\nUser Statistics (user_premium_mcp):")
    user_stats = access_manager.get_access_statistics(user_id="user_premium_mcp")
    print_json(user_stats)
    
    # Test 6: Content limit enforcement
    print_section("6. Testing Content Limit Enforcement")
    
    print("Test: Free user accessing multiple articles (limit: 10)")
    
    free_user_sub = access_manager.get_user_subscription("user_free_mcp")
    if free_user_sub:
        print(f"  Current access count: {free_user_sub.content_accessed_count}")
        
        # Simulate accessing 10 articles
        for i in range(10):
            input_data = CheckContentAccessInput(
                user_id="user_free_mcp",
                content_id=f"article_{i}",
                access_level="public",
                requesting_interface="test_mcp_client"
            )
            
            result = await content_tools.check_content_access(input_data)
            
            if not result.access_granted:
                print(f"  ✗ Access denied at article {i+1}: {result.reason}")
                break
        
        # Check final count
        free_user_sub = access_manager.get_user_subscription("user_free_mcp")
        print(f"  Final access count: {free_user_sub.content_accessed_count}")
        
        # Try one more (should be denied)
        print("\n  Attempting to access article 11 (should be denied):")
        input_data = CheckContentAccessInput(
            user_id="user_free_mcp",
            content_id="article_11",
            access_level="public",
            requesting_interface="test_mcp_client"
        )
        
        result = await content_tools.check_content_access(input_data)
        print(f"    Access Granted: {result.access_granted}")
        print(f"    Reason: {result.reason}")
    
    print_section("Test Complete")
    print("All MCP access control tools integration tests completed!\n")


if __name__ == "__main__":
    asyncio.run(main())
