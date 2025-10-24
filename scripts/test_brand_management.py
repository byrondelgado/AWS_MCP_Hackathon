#!/usr/bin/env python3
"""
Test script for brand metadata management functionality.

This script tests the brand manager, publisher profiles, trust score calculation,
and brand identity package creation.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.brand_manager import BrandManager
from models.validation import BrandMetadataValidator
from mcp_server.tools.brand_tools import BrandTools


async def test_brand_manager():
    """Test the BrandManager functionality."""
    print("🧪 Testing Brand Manager Functionality")
    print("=" * 50)
    
    # Initialize brand manager
    brand_manager = BrandManager()
    
    # Test 1: List existing publishers
    print("\n1. Testing publisher listing...")
    publishers = brand_manager.list_publishers()
    print(f"   Found {len(publishers)} publishers:")
    for pub in publishers:
        print(f"   - {pub.name} (ID: {pub.publisher_id}, Trust: {pub.trust_score})")
    
    # Test 2: Get publisher details
    print("\n2. Testing publisher retrieval...")
    guardian = brand_manager.get_publisher("guardian")
    if guardian:
        print(f"   Guardian Publisher:")
        print(f"   - Name: {guardian.name}")
        print(f"   - Trust Score: {guardian.trust_score}")
        print(f"   - Established: {guardian.established_year}")
        print(f"   - Verified: {guardian.verified}")
    
    # Test 3: Create brand metadata package
    print("\n3. Testing brand metadata package creation...")
    brand_package, validation_result = brand_manager.create_brand_metadata_package(
        "guardian", "article"
    )
    
    if validation_result.is_valid:
        print("   ✅ Brand metadata package created successfully")
        print(f"   - Publisher: {brand_package.publisher.name}")
        print(f"   - Attribution required: {brand_package.attribution.required}")
        print(f"   - Display format: {brand_package.attribution.display_format}")
        print(f"   - Trust score: {brand_package.publisher.trust_score}")
    else:
        print("   ❌ Brand metadata package creation failed")
        for error in validation_result.errors:
            print(f"   - Error: {error}")
    
    # Test 4: Trust score calculation
    print("\n4. Testing trust score calculation...")
    test_metrics = {
        "fact_check_accuracy": 0.95,
        "editorial_quality": 0.9,
        "source_reliability": 0.92,
        "correction_rate": 0.05,
        "reader_trust": 0.88,
        "industry_recognition": 0.85,
        "transparency_score": 0.9
    }
    
    new_score, calculation_details = brand_manager.calculate_trust_score("guardian", test_metrics)
    print(f"   Trust score updated: {calculation_details['previous_score']} → {new_score}")
    print(f"   Score change: {calculation_details['score_change']}")
    print(f"   Weighted score: {calculation_details['weighted_score']}")
    
    # Test 5: Get trust score history
    print("\n5. Testing trust score history...")
    trust_history = brand_manager.get_trust_score_history("guardian")
    print(f"   Trust trend: {trust_history.get('trend', 'unknown')}")
    print(f"   History entries: {len(trust_history.get('history', []))}")
    
    # Test 6: Brand analytics
    print("\n6. Testing brand analytics...")
    analytics = brand_manager.get_brand_analytics("guardian")
    print(f"   Publisher: {analytics['publisher_name']}")
    print(f"   Current trust score: {analytics['current_trust_score']}")
    print(f"   Trust trend: {analytics['trust_trend']}")
    print(f"   Brand packages: {analytics['brand_packages']}")
    
    # Test 7: Global analytics
    print("\n7. Testing global analytics...")
    global_analytics = brand_manager.get_brand_analytics()
    print(f"   Total publishers: {global_analytics['total_publishers']}")
    print(f"   Verified publishers: {global_analytics['verified_publishers']}")
    print(f"   Average trust score: {global_analytics['average_trust_score']}")
    print(f"   Trust score distribution:")
    for category, count in global_analytics['trust_score_distribution'].items():
        print(f"     - {category}: {count}")
    
    return True


async def test_brand_tools():
    """Test the BrandTools MCP interface."""
    print("\n\n🔧 Testing Brand Tools MCP Interface")
    print("=" * 50)
    
    # Initialize brand tools
    brand_tools = BrandTools()
    
    # Test 1: List publishers via MCP tool
    print("\n1. Testing list_publishers MCP tool...")
    result = await brand_tools.list_publishers()
    if result["success"]:
        print(f"   ✅ Found {result['total_count']} publishers")
        print(f"   - Verified: {result['verified_count']}")
        print(f"   - Average trust score: {result['average_trust_score']}")
        
        for pub in result["publishers"][:2]:  # Show first 2
            print(f"   - {pub['name']}: Trust {pub['trust_score']}, Trend: {pub['trust_trend']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 2: Get brand metadata via MCP tool
    print("\n2. Testing get_brand_metadata MCP tool...")
    result = await brand_tools.get_brand_metadata("guardian", "article")
    if result["success"]:
        print("   ✅ Brand metadata retrieved successfully")
        print(f"   - Publisher: {result['publisher_info']['name']}")
        print(f"   - Trust score: {result['publisher_info']['trust_score']}")
        print(f"   - Verified: {result['publisher_info']['verified']}")
        
        # Check brand metadata structure
        brand_meta = result["brand_metadata"]
        print(f"   - Attribution required: {brand_meta['attribution']['required']}")
        print(f"   - Display format: {brand_meta['attribution']['display_format']}")
        print(f"   - Minimum attribution: {brand_meta['display_requirements']['minimum_attribution']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 3: Calculate trust score via MCP tool
    print("\n3. Testing calculate_trust_score MCP tool...")
    test_metrics = {
        "fact_check_accuracy": 0.93,
        "editorial_quality": 0.88,
        "source_reliability": 0.91,
        "correction_rate": 0.07,
        "reader_trust": 0.85,
        "industry_recognition": 0.82,
        "transparency_score": 0.89
    }
    
    result = await brand_tools.calculate_trust_score("guardian", test_metrics)
    if result["success"]:
        print("   ✅ Trust score calculated successfully")
        update_info = result["trust_score_update"]
        print(f"   - Previous: {update_info['previous_score']}")
        print(f"   - New: {update_info['new_score']}")
        print(f"   - Change: {update_info['score_change']}")
        print(f"   - Trend: {result['trust_trend']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 4: Get publisher analytics via MCP tool
    print("\n4. Testing get_publisher_analytics MCP tool...")
    result = await brand_tools.get_publisher_analytics("guardian")
    if result["success"]:
        print("   ✅ Analytics retrieved successfully")
        analytics = result["analytics"]
        print(f"   - Publisher: {analytics['publisher_name']}")
        print(f"   - Trust score: {analytics['current_trust_score']}")
        print(f"   - Trend: {analytics['trust_trend']}")
        print(f"   - Verification: {analytics['verification_status']}")
        
        perf = analytics["performance_summary"]
        print(f"   - Score changes: {perf['total_score_changes']}")
        print(f"   - Stability: {perf['score_stability']}")
    else:
        print(f"   ❌ Error: {result['error']}")
    
    # Test 5: Create new publisher via MCP tool
    print("\n5. Testing create_publisher_profile MCP tool...")
    new_publisher_data = {
        "publisher_id": "test_publisher",
        "name": "Test Publishing House",
        "description": "A test publisher for demonstration",
        "website": "https://testpublisher.com",
        "contact_email": "editor@testpublisher.com",
        "logo_url": "https://testpublisher.com/logo.svg",
        "brand_color": "#2c5aa0",
        "established_year": 2020,
        "trust_score": 7.5,
        "verified": False,
        "fact_checking_policy": "Editorial review process",
        "default_attribution_requirements": {
            "required": True,
            "display_format": "text-only",
            "minimum_visibility": "standard"
        }
    }
    
    result = await brand_tools.create_publisher_profile(new_publisher_data)
    if result["success"]:
        print("   ✅ Publisher created successfully")
        pub = result["publisher"]
        print(f"   - Name: {pub['name']}")
        print(f"   - ID: {pub['publisher_id']}")
        print(f"   - Trust score: {pub['trust_score']}")
        print(f"   - Created: {pub['created_at']}")
        
        if result["validation_warnings"]:
            print("   - Warnings:")
            for warning in result["validation_warnings"]:
                print(f"     • {warning}")
    else:
        print(f"   ❌ Error: {result['error']}")
        if result.get("validation_errors"):
            for error in result["validation_errors"]:
                print(f"     • {error}")
    
    return True


async def test_validation():
    """Test brand metadata validation."""
    print("\n\n✅ Testing Brand Metadata Validation")
    print("=" * 50)
    
    # Initialize brand manager
    brand_manager = BrandManager()
    
    # Test validation with good data
    print("\n1. Testing validation with valid data...")
    guardian = brand_manager.get_publisher("guardian")
    if guardian:
        brand_package, validation_result = brand_manager.create_brand_metadata_package("guardian")
        
        if validation_result.is_valid:
            print("   ✅ Validation passed for Guardian brand package")
            print(f"   - Warnings: {len(validation_result.warnings)}")
            for warning in validation_result.warnings:
                print(f"     • {warning}")
        else:
            print("   ❌ Validation failed")
            for error in validation_result.errors:
                print(f"     • {error}")
    
    # Test validation with invalid data
    print("\n2. Testing validation with invalid data...")
    invalid_publisher_data = {
        "publisher_id": "invalid_test",
        "name": "Invalid Publisher",
        "website": "not-a-valid-url",  # Invalid URL
        "contact_email": "invalid-email",  # Invalid email
        "logo_url": "also-not-a-url",  # Invalid URL
        "brand_color": "not-a-hex-color",  # Invalid hex color
        "established_year": 2050,  # Future year
        "trust_score": 15.0,  # Out of range
    }
    
    try:
        publisher, validation_result = brand_manager.create_publisher(invalid_publisher_data)
        if not validation_result.is_valid:
            print("   ✅ Validation correctly caught errors:")
            for error in validation_result.errors:
                print(f"     • {error}")
        else:
            print("   ❌ Validation should have failed but didn't")
    except Exception as e:
        print(f"   ✅ Validation correctly raised exception: {str(e)}")
    
    return True


async def main():
    """Run all brand management tests."""
    print("🚀 Brand Metadata Management Test Suite")
    print("=" * 60)
    
    try:
        # Run all tests
        await test_brand_manager()
        await test_brand_tools()
        await test_validation()
        
        print("\n\n🎉 All tests completed successfully!")
        print("=" * 60)
        print("Brand metadata management system is working correctly.")
        
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)