"""
Brand-related MCP tools for attribution validation and brand visibility tracking.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import re

try:
    # Try relative imports first (for when running as module)
    from ...schemas.mcp_tools import (
        ValidateAttributionInput,
        ValidateAttributionOutput,
        TrackBrandVisibilityInput,
        TrackBrandVisibilityOutput
    )
    from ...services.brand_manager import BrandManager
except ImportError:
    # Fall back to direct imports (for standalone execution)
    from schemas.mcp_tools import (
        ValidateAttributionInput,
        ValidateAttributionOutput,
        TrackBrandVisibilityInput,
        TrackBrandVisibilityOutput
    )
    from services.brand_manager import BrandManager

logger = logging.getLogger(__name__)


class BrandTools:
    """Tools for brand attribution validation and visibility tracking."""
    
    def __init__(self):
        """Initialize brand tools."""
        self.brand_manager = BrandManager()
        self._visibility_tracking = {}  # In-memory storage for demo
        self._attribution_requirements = self._load_attribution_requirements()
    
    def _load_attribution_requirements(self) -> Dict[str, Dict[str, Any]]:
        """Load attribution requirements for different publishers."""
        return {
            "guardian-climate-2024": {
                "minimum_attribution": "The Guardian | Fact-Checked | Est. 1821",
                "required_badges": ["verified-source", "fact-checked"],
                "minimum_visibility_duration": 5,  # seconds
                "display_format": "badge-with-logo",
                "brand_visibility": "high-prominence"
            }
        }
    
    async def validate_attribution(self, input_data: ValidateAttributionInput) -> ValidateAttributionOutput:
        """
        Validate attribution compliance for displayed content.
        
        Checks if the displayed attribution meets the publisher's requirements
        for brand visibility and compliance.
        """
        try:
            logger.info(f"Validating attribution for content: {input_data.content_id}")
            
            # Get attribution requirements for this content
            requirements = self._attribution_requirements.get(input_data.content_id)
            if not requirements:
                return ValidateAttributionOutput(
                    compliant=False,
                    compliance_score=0.0,
                    violations=["No attribution requirements found for content"],
                    recommendations=["Contact publisher for attribution guidelines"]
                )
            
            violations = []
            recommendations = []
            compliance_factors = {}
            
            # Check minimum attribution text
            min_attribution = requirements["minimum_attribution"]
            if min_attribution not in input_data.displayed_attribution:
                violations.append(f"Missing required attribution text: '{min_attribution}'")
                recommendations.append(f"Include the full attribution: '{min_attribution}'")
                compliance_factors["attribution_text"] = 0.0
            else:
                compliance_factors["attribution_text"] = 1.0
            
            # Check display format
            required_format = requirements["display_format"]
            if input_data.display_format != required_format:
                violations.append(f"Incorrect display format. Required: {required_format}, Used: {input_data.display_format}")
                recommendations.append(f"Use {required_format} format for attribution display")
                compliance_factors["display_format"] = 0.5
            else:
                compliance_factors["display_format"] = 1.0
            
            # Check visibility duration
            min_duration = requirements.get("minimum_visibility_duration", 0)
            if input_data.visibility_duration and input_data.visibility_duration < min_duration:
                violations.append(f"Attribution displayed for insufficient duration. Required: {min_duration}s, Actual: {input_data.visibility_duration}s")
                recommendations.append(f"Display attribution for at least {min_duration} seconds")
                compliance_factors["visibility_duration"] = input_data.visibility_duration / min_duration
            else:
                compliance_factors["visibility_duration"] = 1.0
            
            # Check for required badges
            required_badges = requirements.get("required_badges", [])
            for badge in required_badges:
                if badge not in input_data.displayed_attribution.lower():
                    violations.append(f"Missing required badge: {badge}")
                    recommendations.append(f"Include {badge} badge in attribution")
            
            # Calculate overall compliance score
            compliance_score = sum(compliance_factors.values()) / len(compliance_factors) if compliance_factors else 0.0
            
            # Adjust score based on violations
            if violations:
                compliance_score *= max(0.1, 1.0 - (len(violations) * 0.2))
            
            is_compliant = compliance_score >= 0.8 and len(violations) == 0
            
            logger.info(f"Attribution validation complete. Compliant: {is_compliant}, Score: {compliance_score}")
            
            return ValidateAttributionOutput(
                compliant=is_compliant,
                compliance_score=round(compliance_score, 2),
                violations=violations,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error validating attribution: {str(e)}", exc_info=True)
            return ValidateAttributionOutput(
                compliant=False,
                compliance_score=0.0,
                violations=[f"Validation error: {str(e)}"],
                recommendations=["Contact technical support for assistance"]
            )
    
    async def track_brand_visibility(self, input_data: TrackBrandVisibilityInput) -> TrackBrandVisibilityOutput:
        """
        Track brand visibility and user engagement metrics.
        
        Records how brand elements are displayed and interacted with
        across different AI interfaces.
        """
        try:
            logger.info(f"Tracking brand visibility for content: {input_data.content_id}")
            
            # Generate unique tracking ID
            tracking_id = f"vis_{input_data.content_id}_{input_data.interface}_{datetime.utcnow().timestamp()}"
            
            # Process visibility metrics
            visibility_data = {
                "content_id": input_data.content_id,
                "interface": input_data.interface,
                "timestamp": datetime.utcnow().isoformat(),
                "visibility_metrics": input_data.visibility_metrics,
                "user_interactions": input_data.user_interactions,
                "tracking_id": tracking_id
            }
            
            # Store tracking data (in-memory for demo)
            self._visibility_tracking[tracking_id] = visibility_data
            
            # Analyze compliance status
            compliance_status = self._analyze_visibility_compliance(
                input_data.content_id,
                input_data.visibility_metrics
            )
            
            logger.info(f"Brand visibility tracked: {tracking_id}")
            
            return TrackBrandVisibilityOutput(
                tracking_recorded=True,
                tracking_id=tracking_id,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Error tracking brand visibility: {str(e)}", exc_info=True)
            return TrackBrandVisibilityOutput(
                tracking_recorded=False,
                tracking_id="",
                compliance_status="error"
            )
    
    def _analyze_visibility_compliance(self, content_id: str, visibility_metrics: Dict[str, Any]) -> str:
        """Analyze visibility metrics for compliance status."""
        try:
            requirements = self._attribution_requirements.get(content_id, {})
            
            # Check visibility duration
            duration = visibility_metrics.get("duration_seconds", 0)
            min_duration = requirements.get("minimum_visibility_duration", 0)
            
            if duration < min_duration:
                return "non_compliant"
            
            # Check prominence level
            prominence = visibility_metrics.get("prominence_level", "minimal")
            required_prominence = requirements.get("brand_visibility", "standard")
            
            prominence_levels = {"minimal": 1, "standard": 2, "high-prominence": 3}
            if prominence_levels.get(prominence, 1) < prominence_levels.get(required_prominence, 2):
                return "partial_compliance"
            
            return "compliant"
            
        except Exception:
            return "unknown"
    
    def get_tracking_summary(self, content_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary of brand visibility tracking data."""
        if content_id:
            # Filter by content ID
            relevant_tracking = {
                k: v for k, v in self._visibility_tracking.items() 
                if v["content_id"] == content_id
            }
        else:
            relevant_tracking = self._visibility_tracking
        
        return {
            "total_tracking_events": len(relevant_tracking),
            "interfaces": list(set(v["interface"] for v in relevant_tracking.values())),
            "compliance_summary": self._calculate_compliance_summary(relevant_tracking),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _calculate_compliance_summary(self, tracking_data: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
        """Calculate compliance summary from tracking data."""
        compliance_counts = {"compliant": 0, "partial_compliance": 0, "non_compliant": 0, "unknown": 0}
        
        for data in tracking_data.values():
            content_id = data["content_id"]
            visibility_metrics = data["visibility_metrics"]
            status = self._analyze_visibility_compliance(content_id, visibility_metrics)
            compliance_counts[status] = compliance_counts.get(status, 0) + 1
        
        return compliance_counts
    
    async def get_brand_metadata(self, publisher_id: str, content_type: str = "article") -> Dict[str, Any]:
        """
        Retrieve brand metadata package for a publisher and content type.
        
        Args:
            publisher_id: Publisher identifier
            content_type: Type of content
            
        Returns:
            Brand metadata package or error information
        """
        try:
            logger.info(f"Retrieving brand metadata for publisher: {publisher_id}, content_type: {content_type}")
            
            # Get publisher information
            publisher = self.brand_manager.get_publisher(publisher_id)
            if not publisher:
                return {
                    "success": False,
                    "error": f"Publisher not found: {publisher_id}",
                    "available_publishers": [p.publisher_id for p in self.brand_manager.list_publishers()]
                }
            
            # Get or create brand metadata package
            brand_package = self.brand_manager.get_brand_metadata_package(publisher_id, content_type)
            if not brand_package:
                # Create new package
                brand_package, validation_result = self.brand_manager.create_brand_metadata_package(
                    publisher_id, content_type
                )
                
                if not validation_result.is_valid:
                    return {
                        "success": False,
                        "error": "Failed to create brand metadata package",
                        "validation_errors": validation_result.errors,
                        "validation_warnings": validation_result.warnings
                    }
            
            return {
                "success": True,
                "publisher_id": publisher_id,
                "content_type": content_type,
                "brand_metadata": brand_package.model_dump() if brand_package else None,
                "publisher_info": {
                    "name": publisher.name,
                    "trust_score": publisher.trust_score,
                    "verified": publisher.verified,
                    "established_year": publisher.established_year
                }
            }
            
        except Exception as e:
            logger.error(f"Error retrieving brand metadata: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Brand metadata retrieval failed: {str(e)}"
            }
    
    async def create_publisher_profile(self, publisher_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new publisher profile with brand identity package.
        
        Args:
            publisher_data: Publisher information dictionary
            
        Returns:
            Creation result with publisher information or errors
        """
        try:
            logger.info(f"Creating publisher profile: {publisher_data.get('name', 'Unknown')}")
            
            # Create publisher through brand manager
            publisher, validation_result = self.brand_manager.create_publisher(publisher_data)
            
            if not validation_result.is_valid:
                return {
                    "success": False,
                    "error": "Publisher validation failed",
                    "validation_errors": validation_result.errors,
                    "validation_warnings": validation_result.warnings
                }
            
            # Get brand analytics for the new publisher
            analytics = self.brand_manager.get_brand_analytics(publisher.publisher_id)
            
            return {
                "success": True,
                "publisher": {
                    "publisher_id": publisher.publisher_id,
                    "name": publisher.name,
                    "trust_score": publisher.trust_score,
                    "verified": publisher.verified,
                    "established_year": publisher.established_year,
                    "brand_color": publisher.brand_color,
                    "website": str(publisher.website),
                    "created_at": publisher.created_at.isoformat()
                },
                "brand_analytics": analytics,
                "validation_warnings": validation_result.warnings
            }
            
        except Exception as e:
            logger.error(f"Error creating publisher profile: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Publisher creation failed: {str(e)}"
            }
    
    async def calculate_trust_score(self, publisher_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate and update trust score for a publisher based on performance metrics.
        
        Args:
            publisher_id: Publisher identifier
            metrics: Performance metrics dictionary
            
        Returns:
            Trust score calculation results
        """
        try:
            logger.info(f"Calculating trust score for publisher: {publisher_id}")
            
            # Validate publisher exists
            publisher = self.brand_manager.get_publisher(publisher_id)
            if not publisher:
                return {
                    "success": False,
                    "error": f"Publisher not found: {publisher_id}",
                    "available_publishers": [p.publisher_id for p in self.brand_manager.list_publishers()]
                }
            
            # Calculate new trust score
            new_score, calculation_details = self.brand_manager.calculate_trust_score(publisher_id, metrics)
            
            # Get updated trust score history
            trust_history = self.brand_manager.get_trust_score_history(publisher_id)
            
            return {
                "success": True,
                "publisher_id": publisher_id,
                "publisher_name": publisher.name,
                "trust_score_update": {
                    "previous_score": calculation_details['previous_score'],
                    "new_score": new_score,
                    "score_change": calculation_details['score_change'],
                    "calculation_timestamp": calculation_details['calculation_timestamp']
                },
                "calculation_details": calculation_details,
                "trust_trend": trust_history.get('trend', 'unknown'),
                "score_history_length": len(trust_history.get('history', []))
            }
            
        except Exception as e:
            logger.error(f"Error calculating trust score: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Trust score calculation failed: {str(e)}"
            }
    
    async def get_publisher_analytics(self, publisher_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get brand analytics and performance metrics for publishers.
        
        Args:
            publisher_id: Optional publisher identifier (if None, returns global analytics)
            
        Returns:
            Analytics data for publisher(s)
        """
        try:
            logger.info(f"Retrieving analytics for publisher: {publisher_id or 'all'}")
            
            # Get analytics from brand manager
            analytics = self.brand_manager.get_brand_analytics(publisher_id)
            
            if publisher_id and "error" in analytics:
                return {
                    "success": False,
                    "error": analytics["error"],
                    "available_publishers": [p.publisher_id for p in self.brand_manager.list_publishers()]
                }
            
            return {
                "success": True,
                "analytics": analytics,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving analytics: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Analytics retrieval failed: {str(e)}"
            }
    
    async def list_publishers(self) -> Dict[str, Any]:
        """
        List all registered publishers with their basic information.
        
        Returns:
            List of publishers with key information
        """
        try:
            logger.info("Listing all publishers")
            
            publishers = self.brand_manager.list_publishers()
            
            publisher_list = []
            for publisher in publishers:
                trust_history = self.brand_manager.get_trust_score_history(publisher.publisher_id)
                
                publisher_list.append({
                    "publisher_id": publisher.publisher_id,
                    "name": publisher.name,
                    "trust_score": publisher.trust_score,
                    "trust_trend": trust_history.get('trend', 'unknown'),
                    "verified": publisher.verified,
                    "established_year": publisher.established_year,
                    "brand_color": publisher.brand_color,
                    "website": str(publisher.website),
                    "created_at": publisher.created_at.isoformat(),
                    "last_updated": publisher.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "publishers": publisher_list,
                "total_count": len(publisher_list),
                "verified_count": sum(1 for p in publisher_list if p["verified"]),
                "average_trust_score": round(sum(p["trust_score"] for p in publisher_list) / len(publisher_list), 2) if publisher_list else 0
            }
            
        except Exception as e:
            logger.error(f"Error listing publishers: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Publisher listing failed: {str(e)}"
            }