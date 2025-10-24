"""
Brand-related MCP tools for attribution validation and brand visibility tracking.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import re

from ...schemas.mcp_tools import (
    ValidateAttributionInput,
    ValidateAttributionOutput,
    TrackBrandVisibilityInput,
    TrackBrandVisibilityOutput
)

logger = logging.getLogger(__name__)


class BrandTools:
    """Tools for brand attribution validation and visibility tracking."""
    
    def __init__(self):
        """Initialize brand tools."""
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