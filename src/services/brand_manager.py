"""
Brand metadata management service for content publishing MCP server.

This service handles brand metadata storage, retrieval, publisher profile management,
brand identity package creation, and trust score calculation.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import hashlib
from pathlib import Path

try:
    # Try relative imports first (for when running as module)
    from ..models.brand import (
        BrandMetadata, PublisherMetadata, AttributionRequirements,
        EditorialMetadata, RightsMetadata, ContentCuration, DisplayRequirements
    )
    from ..models.content import Publisher, ContentType
    from ..models.validation import BrandMetadataValidator, ValidationResult
    from ..mcp_server.config import get_config
except ImportError:
    # Fall back to direct imports (for standalone execution)
    from models.brand import (
        BrandMetadata, PublisherMetadata, AttributionRequirements,
        EditorialMetadata, RightsMetadata, ContentCuration, DisplayRequirements
    )
    from models.content import Publisher, ContentType
    from models.validation import BrandMetadataValidator, ValidationResult
    from mcp_server.config import get_config

logger = logging.getLogger(__name__)


class BrandManager:
    """Manages brand metadata, publisher profiles, and trust scores."""
    
    def __init__(self):
        """Initialize brand manager with storage backend."""
        self.config = get_config()
        self._publishers = {}  # In-memory storage for demo
        self._brand_packages = {}  # Brand identity packages
        self._trust_scores = {}  # Trust score tracking
        self._attribution_templates = {}  # Attribution requirement templates
        
        # Initialize with sample publisher data
        self._initialize_sample_publishers()
    
    def _initialize_sample_publishers(self):
        """Initialize with sample publisher profiles (Guardian, Industry, Hachette)."""
        sample_publishers = [
            {
                "publisher_id": "guardian",
                "name": "The Guardian",
                "description": "Independent journalism since 1821",
                "website": "https://theguardian.com",
                "contact_email": "editorial@theguardian.com",
                "logo_url": "https://assets.theguardian.com/logo-badge.svg",
                "brand_color": "#052962",
                "established_year": 1821,
                "trust_score": 9.2,
                "verified": True,
                "verification_date": datetime(2024, 1, 15),
                "editorial_standards_url": "https://theguardian.com/editorial-code",
                "fact_checking_policy": "Triple-sourced investigative reporting with independent fact-checking",
                "default_attribution_requirements": {
                    "required": True,
                    "display_format": "badge-with-logo",
                    "minimum_visibility": "prominent",
                    "minimum_duration": 5
                },
                "content_licensing_terms": {
                    "ai_training": "ai-training-permitted",
                    "attribution": "mandatory",
                    "modification": "summary-only"
                }
            },
            {
                "publisher_id": "industry",
                "name": "Industry Publications",
                "description": "Professional industry analysis and reporting",
                "website": "https://industry-pub.com",
                "contact_email": "editor@industry-pub.com",
                "logo_url": "https://industry-pub.com/assets/logo.svg",
                "brand_color": "#1a472a",
                "established_year": 1995,
                "trust_score": 8.7,
                "verified": True,
                "verification_date": datetime(2024, 2, 20),
                "editorial_standards_url": "https://industry-pub.com/standards",
                "fact_checking_policy": "Industry expert review and verification",
                "default_attribution_requirements": {
                    "required": True,
                    "display_format": "text-only",
                    "minimum_visibility": "standard",
                    "minimum_duration": 3
                },
                "content_licensing_terms": {
                    "ai_training": "ai-training-permitted",
                    "attribution": "mandatory",
                    "modification": "excerpts-allowed"
                }
            },
            {
                "publisher_id": "hachette",
                "name": "Hachette Book Group",
                "description": "Global publisher of books and digital content",
                "website": "https://hachettebookgroup.com",
                "contact_email": "rights@hachette.com",
                "logo_url": "https://hachette.com/assets/brand-logo.svg",
                "brand_color": "#c41e3a",
                "established_year": 1826,
                "trust_score": 8.9,
                "verified": True,
                "verification_date": datetime(2024, 1, 10),
                "editorial_standards_url": "https://hachette.com/editorial-standards",
                "fact_checking_policy": "Editorial review and author verification process",
                "default_attribution_requirements": {
                    "required": True,
                    "display_format": "badge-with-logo",
                    "minimum_visibility": "prominent",
                    "minimum_duration": 7
                },
                "content_licensing_terms": {
                    "ai_training": "ai-training-restricted",
                    "attribution": "mandatory",
                    "modification": "no-modification"
                }
            }
        ]
        
        for pub_data in sample_publishers:
            publisher = Publisher(**pub_data)
            self._publishers[publisher.publisher_id] = publisher
            
            # Create brand identity packages
            self._create_brand_identity_package(publisher)
            
            # Initialize trust score tracking
            self._initialize_trust_score_tracking(publisher.publisher_id, publisher.trust_score)
        
        logger.info(f"Initialized {len(sample_publishers)} sample publishers")
    
    def get_publisher(self, publisher_id: str) -> Optional[Publisher]:
        """Retrieve publisher profile by ID."""
        return self._publishers.get(publisher_id)
    
    def list_publishers(self) -> List[Publisher]:
        """List all registered publishers."""
        return list(self._publishers.values())
    
    def create_publisher(self, publisher_data: Dict[str, Any]) -> Tuple[Publisher, ValidationResult]:
        """
        Create a new publisher profile with validation.
        
        Args:
            publisher_data: Publisher information dictionary
            
        Returns:
            Tuple of (Publisher instance, ValidationResult)
        """
        try:
            # Create publisher instance
            publisher = Publisher(**publisher_data)
            
            # Validate publisher data
            validation_result = BrandMetadataValidator._validate_publisher(
                PublisherMetadata(
                    name=publisher.name,
                    logo=publisher.logo_url,
                    brand_color=publisher.brand_color,
                    trust_score=publisher.trust_score,
                    established_year=publisher.established_year,
                    website=publisher.website
                )
            )
            
            if validation_result.is_valid:
                # Store publisher
                self._publishers[publisher.publisher_id] = publisher
                
                # Create brand identity package
                self._create_brand_identity_package(publisher)
                
                # Initialize trust score tracking
                self._initialize_trust_score_tracking(publisher.publisher_id, publisher.trust_score)
                
                logger.info(f"Created publisher: {publisher.name} ({publisher.publisher_id})")
            
            return publisher, validation_result
            
        except Exception as e:
            logger.error(f"Error creating publisher: {str(e)}", exc_info=True)
            validation_result = ValidationResult(False)
            validation_result.add_error(f"Publisher creation failed: {str(e)}")
            return None, validation_result
    
    def update_publisher(self, publisher_id: str, updates: Dict[str, Any]) -> Tuple[Optional[Publisher], ValidationResult]:
        """
        Update publisher profile with validation.
        
        Args:
            publisher_id: Publisher identifier
            updates: Dictionary of fields to update
            
        Returns:
            Tuple of (updated Publisher or None, ValidationResult)
        """
        publisher = self._publishers.get(publisher_id)
        if not publisher:
            validation_result = ValidationResult(False)
            validation_result.add_error(f"Publisher not found: {publisher_id}")
            return None, validation_result
        
        try:
            # Create updated publisher data
            publisher_dict = publisher.model_dump()
            publisher_dict.update(updates)
            publisher_dict['updated_at'] = datetime.utcnow()
            
            # Create new publisher instance
            updated_publisher = Publisher(**publisher_dict)
            
            # Validate updated data
            validation_result = BrandMetadataValidator._validate_publisher(
                PublisherMetadata(
                    name=updated_publisher.name,
                    logo=updated_publisher.logo_url,
                    brand_color=updated_publisher.brand_color,
                    trust_score=updated_publisher.trust_score,
                    established_year=updated_publisher.established_year,
                    website=updated_publisher.website
                )
            )
            
            if validation_result.is_valid:
                # Update stored publisher
                self._publishers[publisher_id] = updated_publisher
                
                # Update brand identity package
                self._create_brand_identity_package(updated_publisher)
                
                # Update trust score if changed
                if 'trust_score' in updates:
                    self._update_trust_score(publisher_id, updates['trust_score'])
                
                logger.info(f"Updated publisher: {publisher_id}")
            
            return updated_publisher, validation_result
            
        except Exception as e:
            logger.error(f"Error updating publisher {publisher_id}: {str(e)}", exc_info=True)
            validation_result = ValidationResult(False)
            validation_result.add_error(f"Publisher update failed: {str(e)}")
            return None, validation_result
    
    def create_brand_metadata_package(
        self, 
        publisher_id: str, 
        content_type: str = "article",
        custom_requirements: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[BrandMetadata], ValidationResult]:
        """
        Create a complete brand metadata package for content.
        
        Args:
            publisher_id: Publisher identifier
            content_type: Type of content (article, blog_post, etc.)
            custom_requirements: Custom attribution/rights requirements
            
        Returns:
            Tuple of (BrandMetadata package or None, ValidationResult)
        """
        publisher = self._publishers.get(publisher_id)
        if not publisher:
            validation_result = ValidationResult(False)
            validation_result.add_error(f"Publisher not found: {publisher_id}")
            return None, validation_result
        
        try:
            # Create publisher metadata
            publisher_metadata = PublisherMetadata(
                name=publisher.name,
                logo=publisher.logo_url,
                brand_color=publisher.brand_color,
                trust_score=publisher.trust_score,
                established_year=publisher.established_year,
                website=publisher.website
            )
            
            # Create attribution requirements
            default_attr = publisher.default_attribution_requirements
            attribution_requirements = AttributionRequirements(
                required=custom_requirements.get('required', default_attr.get('required', True)),
                display_format=custom_requirements.get('display_format', default_attr.get('display_format', 'badge-with-logo')),
                minimum_visibility=custom_requirements.get('minimum_visibility', default_attr.get('minimum_visibility', 'prominent')),
                linkback=custom_requirements.get('linkback', f"{publisher.website}/content"),
                duration_seconds=custom_requirements.get('duration_seconds', default_attr.get('minimum_duration'))
            ) if custom_requirements else AttributionRequirements(
                required=default_attr.get('required', True),
                display_format=default_attr.get('display_format', 'badge-with-logo'),
                minimum_visibility=default_attr.get('minimum_visibility', 'prominent'),
                linkback=f"{publisher.website}/content",
                duration_seconds=default_attr.get('minimum_duration')
            )
            
            # Create editorial metadata
            editorial_metadata = EditorialMetadata(
                fact_checked=publisher.fact_checking_policy is not None,
                fact_check_date=datetime.utcnow() if publisher.fact_checking_policy else None,
                editorial_standards=publisher.editorial_standards_url,
                journalist_credentials=[],
                verification_level="triple-sourced" if publisher.trust_score >= 9.0 else "double-sourced",
                editorial_process=publisher.fact_checking_policy
            )
            
            # Create rights metadata
            licensing_terms = publisher.content_licensing_terms
            rights_metadata = RightsMetadata(
                usage=licensing_terms.get('ai_training', 'ai-training-permitted'),
                attribution=licensing_terms.get('attribution', 'mandatory'),
                modification=licensing_terms.get('modification', 'summary-only'),
                commercial_use=licensing_terms.get('commercial_use', 'licensed')
            )
            
            # Create content curation metadata
            curation_metadata = ContentCuration(
                content_type=content_type,
                expertise=[],
                verification_level=editorial_metadata.verification_level,
                editorial_process=publisher.fact_checking_policy
            )
            
            # Create display requirements (map attribution visibility to display visibility)
            visibility_mapping = {
                'prominent': 'high-prominence',
                'standard': 'standard',
                'minimal': 'minimal'
            }
            attr_visibility = default_attr.get('minimum_visibility', 'standard')
            display_visibility = visibility_mapping.get(attr_visibility, 'standard')
            
            display_requirements = DisplayRequirements(
                badges=self._generate_badges(publisher),
                minimum_attribution=f"{publisher.name} | Est. {publisher.established_year}",
                brand_visibility=display_visibility,
                interactive_elements={
                    "allowSaveToPublisher": True,
                    "allowSubscriptionPrompt": True,
                    "allowNewsletterSignup": True
                }
            )
            
            # Create complete brand metadata package
            brand_metadata = BrandMetadata(
                publisher=publisher_metadata,
                attribution=attribution_requirements,
                editorial=editorial_metadata,
                rights=rights_metadata,
                curation=curation_metadata,
                display_requirements=display_requirements
            )
            
            # Validate the complete package
            validation_result = BrandMetadataValidator.validate_brand_metadata(brand_metadata)
            
            if validation_result.is_valid:
                # Store the package
                package_id = self._generate_package_id(publisher_id, content_type)
                self._brand_packages[package_id] = brand_metadata
                
                logger.info(f"Created brand metadata package: {package_id}")
            
            return brand_metadata, validation_result
            
        except Exception as e:
            logger.error(f"Error creating brand metadata package: {str(e)}", exc_info=True)
            validation_result = ValidationResult(False)
            validation_result.add_error(f"Brand package creation failed: {str(e)}")
            return None, validation_result
    
    def get_brand_metadata_package(self, publisher_id: str, content_type: str = "article") -> Optional[BrandMetadata]:
        """Retrieve brand metadata package."""
        package_id = self._generate_package_id(publisher_id, content_type)
        return self._brand_packages.get(package_id)
    
    def calculate_trust_score(
        self, 
        publisher_id: str, 
        metrics: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate updated trust score based on performance metrics.
        
        Args:
            publisher_id: Publisher identifier
            metrics: Performance metrics dictionary
            
        Returns:
            Tuple of (new trust score, calculation details)
        """
        current_score = self._trust_scores.get(publisher_id, {}).get('current_score', 5.0)
        
        # Trust score calculation factors
        factors = {
            'fact_check_accuracy': metrics.get('fact_check_accuracy', 0.8),  # 0-1
            'editorial_quality': metrics.get('editorial_quality', 0.7),      # 0-1
            'source_reliability': metrics.get('source_reliability', 0.8),    # 0-1
            'correction_rate': 1.0 - metrics.get('correction_rate', 0.1),    # Lower is better
            'reader_trust': metrics.get('reader_trust', 0.7),                # 0-1
            'industry_recognition': metrics.get('industry_recognition', 0.6), # 0-1
            'transparency_score': metrics.get('transparency_score', 0.8),     # 0-1
        }
        
        # Weighted calculation
        weights = {
            'fact_check_accuracy': 0.25,
            'editorial_quality': 0.20,
            'source_reliability': 0.20,
            'correction_rate': 0.15,
            'reader_trust': 0.10,
            'industry_recognition': 0.05,
            'transparency_score': 0.05
        }
        
        # Calculate weighted score (0-1 range)
        weighted_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        # Convert to 0-10 scale
        new_base_score = weighted_score * 10
        
        # Apply momentum (gradual change from current score)
        momentum_factor = 0.3  # How much the score can change at once
        score_change = (new_base_score - current_score) * momentum_factor
        new_score = current_score + score_change
        
        # Ensure score stays within bounds
        new_score = max(0.0, min(10.0, new_score))
        new_score = round(new_score, 1)
        
        # Update trust score tracking
        self._update_trust_score(publisher_id, new_score, factors)
        
        calculation_details = {
            'previous_score': current_score,
            'new_score': new_score,
            'score_change': round(score_change, 2),
            'factors': factors,
            'weights': weights,
            'weighted_score': round(weighted_score, 3),
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Calculated trust score for {publisher_id}: {current_score} -> {new_score}")
        
        return new_score, calculation_details
    
    def get_trust_score_history(self, publisher_id: str) -> Dict[str, Any]:
        """Get trust score history and trends for a publisher."""
        return self._trust_scores.get(publisher_id, {})
    
    def _create_brand_identity_package(self, publisher: Publisher):
        """Create brand identity package for a publisher."""
        package_id = f"brand_{publisher.publisher_id}"
        
        identity_package = {
            'publisher_id': publisher.publisher_id,
            'brand_elements': {
                'primary_logo': str(publisher.logo_url),
                'brand_color': publisher.brand_color,
                'typography': 'system-ui, -apple-system, sans-serif',
                'badge_style': 'rounded',
                'icon_style': 'filled'
            },
            'attribution_templates': {
                'minimal': f"{publisher.name}",
                'standard': f"{publisher.name} | Est. {publisher.established_year}",
                'full': f"{publisher.name} | Verified Source | Est. {publisher.established_year}",
                'with_trust': f"{publisher.name} | Trust Score: {publisher.trust_score}/10 | Est. {publisher.established_year}"
            },
            'display_guidelines': {
                'minimum_logo_size': '24px',
                'minimum_text_size': '12px',
                'contrast_requirements': 'WCAG AA',
                'animation_allowed': True,
                'interaction_enabled': True
            },
            'created_at': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
        
        self._brand_packages[package_id] = identity_package
    
    def _initialize_trust_score_tracking(self, publisher_id: str, initial_score: float):
        """Initialize trust score tracking for a publisher."""
        self._trust_scores[publisher_id] = {
            'current_score': initial_score,
            'initial_score': initial_score,
            'history': [{
                'score': initial_score,
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'initialization'
            }],
            'factors_history': [],
            'trend': 'stable',
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def _update_trust_score(self, publisher_id: str, new_score: float, factors: Optional[Dict[str, float]] = None):
        """Update trust score tracking."""
        if publisher_id not in self._trust_scores:
            self._initialize_trust_score_tracking(publisher_id, new_score)
            return
        
        tracking = self._trust_scores[publisher_id]
        previous_score = tracking['current_score']
        
        # Update current score
        tracking['current_score'] = new_score
        tracking['last_updated'] = datetime.utcnow().isoformat()
        
        # Add to history
        tracking['history'].append({
            'score': new_score,
            'previous_score': previous_score,
            'change': round(new_score - previous_score, 2),
            'timestamp': datetime.utcnow().isoformat(),
            'event': 'calculation_update'
        })
        
        # Add factors if provided
        if factors:
            tracking['factors_history'].append({
                'factors': factors,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Calculate trend
        if len(tracking['history']) >= 3:
            recent_scores = [h['score'] for h in tracking['history'][-3:]]
            if all(recent_scores[i] <= recent_scores[i+1] for i in range(len(recent_scores)-1)):
                tracking['trend'] = 'improving'
            elif all(recent_scores[i] >= recent_scores[i+1] for i in range(len(recent_scores)-1)):
                tracking['trend'] = 'declining'
            else:
                tracking['trend'] = 'stable'
        
        # Update publisher trust score
        if publisher_id in self._publishers:
            self._publishers[publisher_id].trust_score = new_score
    
    def _generate_badges(self, publisher: Publisher) -> List[str]:
        """Generate appropriate badges for a publisher."""
        badges = []
        
        if publisher.verified:
            badges.append("verified-source")
        
        if publisher.fact_checking_policy:
            badges.append("fact-checked")
        
        if publisher.trust_score >= 9.0:
            badges.append("award-winning-journalism")
        elif publisher.trust_score >= 8.0:
            badges.append("trusted-source")
        
        if publisher.established_year <= 1900:
            badges.append("established-heritage")
        
        return badges
    
    def _generate_package_id(self, publisher_id: str, content_type: str) -> str:
        """Generate unique package ID."""
        return f"{publisher_id}_{content_type}_{hashlib.md5(f'{publisher_id}{content_type}'.encode()).hexdigest()[:8]}"
    
    def get_brand_analytics(self, publisher_id: Optional[str] = None) -> Dict[str, Any]:
        """Get brand analytics and performance metrics."""
        if publisher_id:
            publisher = self._publishers.get(publisher_id)
            if not publisher:
                return {"error": f"Publisher not found: {publisher_id}"}
            
            trust_history = self.get_trust_score_history(publisher_id)
            
            return {
                "publisher_id": publisher_id,
                "publisher_name": publisher.name,
                "current_trust_score": publisher.trust_score,
                "trust_trend": trust_history.get('trend', 'unknown'),
                "verification_status": publisher.verified,
                "brand_packages": len([p for p in self._brand_packages.keys() if p.startswith(publisher_id)]),
                "last_updated": trust_history.get('last_updated'),
                "performance_summary": {
                    "total_score_changes": len(trust_history.get('history', [])) - 1,
                    "score_stability": self._calculate_score_stability(trust_history.get('history', [])),
                    "verification_date": publisher.verification_date.isoformat() if publisher.verification_date else None
                }
            }
        else:
            # Global analytics
            total_publishers = len(self._publishers)
            verified_publishers = sum(1 for p in self._publishers.values() if p.verified)
            avg_trust_score = sum(p.trust_score for p in self._publishers.values()) / total_publishers if total_publishers > 0 else 0
            
            return {
                "total_publishers": total_publishers,
                "verified_publishers": verified_publishers,
                "verification_rate": verified_publishers / total_publishers if total_publishers > 0 else 0,
                "average_trust_score": round(avg_trust_score, 2),
                "total_brand_packages": len(self._brand_packages),
                "trust_score_distribution": self._get_trust_score_distribution(),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    def _calculate_score_stability(self, history: List[Dict[str, Any]]) -> str:
        """Calculate trust score stability rating."""
        if len(history) < 3:
            return "insufficient_data"
        
        changes = [abs(h.get('change', 0)) for h in history if 'change' in h]
        if not changes:
            return "stable"
        
        avg_change = sum(changes) / len(changes)
        
        if avg_change < 0.1:
            return "very_stable"
        elif avg_change < 0.3:
            return "stable"
        elif avg_change < 0.5:
            return "moderate"
        else:
            return "volatile"
    
    def _get_trust_score_distribution(self) -> Dict[str, int]:
        """Get distribution of trust scores across publishers."""
        distribution = {
            "excellent (9.0-10.0)": 0,
            "very_good (8.0-8.9)": 0,
            "good (7.0-7.9)": 0,
            "fair (6.0-6.9)": 0,
            "poor (0.0-5.9)": 0
        }
        
        for publisher in self._publishers.values():
            score = publisher.trust_score
            if score >= 9.0:
                distribution["excellent (9.0-10.0)"] += 1
            elif score >= 8.0:
                distribution["very_good (8.0-8.9)"] += 1
            elif score >= 7.0:
                distribution["good (7.0-7.9)"] += 1
            elif score >= 6.0:
                distribution["fair (6.0-6.9)"] += 1
            else:
                distribution["poor (0.0-5.9)"] += 1
        
        return distribution