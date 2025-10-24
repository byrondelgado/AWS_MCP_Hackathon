"""
Validation utilities for brand metadata standards.

This module provides validation functions for brand metadata standards
including ONIX compliance, ISBN validation, and content quality checks.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pydantic import ValidationError

from .brand import BrandMetadata, PublisherMetadata, AttributionRequirements
from .content import Article, Publisher, ContentType


class ValidationResult:
    """Result of a validation operation."""
    
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        """Add an error to the validation result."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the validation result."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class ISBNValidator:
    """Validator for ISBN-13 format and check digits."""
    
    @staticmethod
    def validate_isbn13(isbn: str) -> ValidationResult:
        """
        Validate ISBN-13 format and check digit.
        
        Args:
            isbn: ISBN string to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(True)
        
        # Remove hyphens and spaces
        clean_isbn = re.sub(r'[-\s]', '', isbn)
        
        # Check length
        if len(clean_isbn) != 13:
            result.add_error(f"ISBN must be 13 digits, got {len(clean_isbn)}")
            return result
        
        # Check if all characters are digits
        if not clean_isbn.isdigit():
            result.add_error("ISBN must contain only digits")
            return result
        
        # Check prefix (must start with 978 or 979)
        if not clean_isbn.startswith(('978', '979')):
            result.add_error("ISBN-13 must start with 978 or 979")
            return result
        
        # Validate check digit
        if not ISBNValidator._validate_check_digit(clean_isbn):
            result.add_error("Invalid ISBN-13 check digit")
        
        return result
    
    @staticmethod
    def _validate_check_digit(isbn: str) -> bool:
        """Validate ISBN-13 check digit using modulo 10 algorithm."""
        total = 0
        for i, digit in enumerate(isbn[:-1]):  # Exclude check digit
            multiplier = 1 if i % 2 == 0 else 3
            total += int(digit) * multiplier
        
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(isbn[-1])
    
    @staticmethod
    def format_isbn(isbn: str) -> str:
        """Format ISBN with standard hyphens."""
        clean_isbn = re.sub(r'[-\s]', '', isbn)
        if len(clean_isbn) == 13:
            return f"{clean_isbn[:3]}-{clean_isbn[3]}-{clean_isbn[4:9]}-{clean_isbn[9:12]}-{clean_isbn[12]}"
        return isbn


class BrandMetadataValidator:
    """Validator for brand metadata standards compliance."""
    
    @staticmethod
    def validate_brand_metadata(metadata: BrandMetadata) -> ValidationResult:
        """
        Validate complete brand metadata package.
        
        Args:
            metadata: BrandMetadata instance to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(True)
        
        # Validate publisher metadata
        publisher_result = BrandMetadataValidator._validate_publisher(metadata.publisher)
        result.errors.extend(publisher_result.errors)
        result.warnings.extend(publisher_result.warnings)
        
        # Validate attribution requirements
        attribution_result = BrandMetadataValidator._validate_attribution(metadata.attribution)
        result.errors.extend(attribution_result.errors)
        result.warnings.extend(attribution_result.warnings)
        
        # Validate editorial metadata
        editorial_result = BrandMetadataValidator._validate_editorial(metadata.editorial)
        result.errors.extend(editorial_result.errors)
        result.warnings.extend(editorial_result.warnings)
        
        # Validate rights metadata
        rights_result = BrandMetadataValidator._validate_rights(metadata.rights)
        result.errors.extend(rights_result.errors)
        result.warnings.extend(rights_result.warnings)
        
        # Check for consistency issues
        consistency_result = BrandMetadataValidator._validate_consistency(metadata)
        result.errors.extend(consistency_result.errors)
        result.warnings.extend(consistency_result.warnings)
        
        if result.errors:
            result.is_valid = False
        
        return result
    
    @staticmethod
    def _validate_publisher(publisher: PublisherMetadata) -> ValidationResult:
        """Validate publisher metadata."""
        result = ValidationResult(True)
        
        # Check trust score range
        if not 0.0 <= publisher.trust_score <= 10.0:
            result.add_error(f"Trust score must be between 0.0 and 10.0, got {publisher.trust_score}")
        
        # Check established year
        current_year = datetime.now().year
        if publisher.established_year > current_year:
            result.add_error(f"Established year cannot be in the future: {publisher.established_year}")
        
        if publisher.established_year < 1400:
            result.add_warning(f"Established year seems very old: {publisher.established_year}")
        
        # Validate brand color format
        if not re.match(r'^#[0-9A-Fa-f]{6}$', publisher.brand_color):
            result.add_error(f"Invalid brand color format: {publisher.brand_color}")
        
        return result
    
    @staticmethod
    def _validate_attribution(attribution: AttributionRequirements) -> ValidationResult:
        """Validate attribution requirements."""
        result = ValidationResult(True)
        
        # Check duration if specified
        if attribution.duration_seconds is not None:
            if attribution.duration_seconds < 1:
                result.add_error("Attribution duration must be at least 1 second")
            elif attribution.duration_seconds > 3600:  # 1 hour
                result.add_warning("Attribution duration longer than 1 hour may be excessive")
        
        return result
    
    @staticmethod
    def _validate_editorial(editorial) -> ValidationResult:
        """Validate editorial metadata."""
        result = ValidationResult(True)
        
        # Check fact-check date consistency
        if editorial.fact_checked and not editorial.fact_check_date:
            result.add_warning("Content marked as fact-checked but no fact-check date provided")
        
        if editorial.fact_check_date and not editorial.fact_checked:
            result.add_error("Fact-check date provided but content not marked as fact-checked")
        
        # Check fact-check date is not in the future
        if editorial.fact_check_date and editorial.fact_check_date > datetime.utcnow():
            result.add_error("Fact-check date cannot be in the future")
        
        return result
    
    @staticmethod
    def _validate_rights(rights) -> ValidationResult:
        """Validate rights metadata."""
        result = ValidationResult(True)
        
        # Check embargo date
        if rights.embargo_date and rights.embargo_date < datetime.utcnow():
            result.add_warning("Embargo date is in the past")
        
        # Validate territory restrictions (should be ISO country codes)
        for territory in rights.territory_restrictions:
            if len(territory) != 2 or not territory.isalpha():
                result.add_warning(f"Territory code should be ISO 3166-1 alpha-2: {territory}")
        
        return result
    
    @staticmethod
    def _validate_consistency(metadata: BrandMetadata) -> ValidationResult:
        """Validate consistency across metadata fields."""
        result = ValidationResult(True)
        
        # Check if attribution is required but display requirements don't enforce it
        if metadata.attribution.required and not metadata.display_requirements.minimum_attribution:
            result.add_error("Attribution is required but no minimum attribution text specified")
        
        # Check if fact-checked content has appropriate trust score
        if metadata.editorial.fact_checked and metadata.publisher.trust_score < 5.0:
            result.add_warning("Fact-checked content from publisher with low trust score")
        
        return result


class ContentValidator:
    """Validator for content models and structure."""
    
    @staticmethod
    def validate_article(article: Article) -> ValidationResult:
        """
        Validate article content and metadata.
        
        Args:
            article: Article instance to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(True)
        
        # Validate content length
        if len(article.text.strip()) < 100:
            result.add_warning("Article text is very short (less than 100 characters)")
        
        # Check title length
        if len(article.title) > 200:
            result.add_warning("Article title is very long (over 200 characters)")
        
        # Validate publish date
        if article.publish_date and article.publish_date > datetime.utcnow():
            result.add_error("Publish date cannot be in the future")
        
        # Check status consistency
        if article.status == "published" and not article.publish_date:
            result.add_error("Published articles must have a publish date")
        
        # Validate authors
        if not article.authors:
            result.add_warning("Article has no authors specified")
        
        # Validate brand metadata
        brand_result = BrandMetadataValidator.validate_brand_metadata(article.brand_metadata)
        result.errors.extend(brand_result.errors)
        result.warnings.extend(brand_result.warnings)
        
        if result.errors:
            result.is_valid = False
        
        return result
    
    @staticmethod
    def validate_publisher(publisher: Publisher) -> ValidationResult:
        """
        Validate publisher profile.
        
        Args:
            publisher: Publisher instance to validate
            
        Returns:
            ValidationResult with validation status and any errors
        """
        result = ValidationResult(True)
        
        # Validate trust score
        if not 0.0 <= publisher.trust_score <= 10.0:
            result.add_error(f"Trust score must be between 0.0 and 10.0, got {publisher.trust_score}")
        
        # Check established year
        current_year = datetime.now().year
        if publisher.established_year > current_year:
            result.add_error(f"Established year cannot be in the future: {publisher.established_year}")
        
        # Validate brand color
        if not re.match(r'^#[0-9A-Fa-f]{6}$', publisher.brand_color):
            result.add_error(f"Invalid brand color format: {publisher.brand_color}")
        
        # Check verification consistency
        if publisher.verified and not publisher.verification_date:
            result.add_warning("Publisher marked as verified but no verification date provided")
        
        if result.errors:
            result.is_valid = False
        
        return result


# Validation utility functions
def validate_content_quality(content: str) -> ValidationResult:
    """Validate content quality metrics."""
    result = ValidationResult(True)
    
    # Check for minimum content length
    if len(content.strip()) < 50:
        result.add_error("Content too short for quality assessment")
        return result
    
    # Check for basic quality indicators
    sentences = content.split('.')
    if len(sentences) < 3:
        result.add_warning("Content has very few sentences")
    
    # Check for excessive repetition
    words = content.lower().split()
    word_count = len(words)
    unique_words = len(set(words))
    
    if word_count > 0 and unique_words / word_count < 0.3:
        result.add_warning("Content has high word repetition")
    
    return result


def validate_metadata_completeness(metadata: Dict[str, Any]) -> ValidationResult:
    """Validate metadata completeness for publishing standards."""
    result = ValidationResult(True)
    
    required_fields = [
        'title', 'publisher', 'content_type', 'language'
    ]
    
    for field in required_fields:
        if field not in metadata or not metadata[field]:
            result.add_error(f"Required metadata field missing: {field}")
    
    recommended_fields = [
        'author', 'publish_date', 'summary', 'tags'
    ]
    
    for field in recommended_fields:
        if field not in metadata or not metadata[field]:
            result.add_warning(f"Recommended metadata field missing: {field}")
    
    if result.errors:
        result.is_valid = False
    
    return result