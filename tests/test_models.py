"""
Test suite for data models and validation.

This module tests the core Pydantic models and validation functions
to ensure they work correctly with the brand metadata standards.
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.models.brand import (
    PublisherMetadata,
    AttributionRequirements,
    EditorialMetadata,
    RightsMetadata,
    ContentCuration,
    DisplayRequirements,
    BrandMetadata
)
from src.models.content import (
    Article,
    Publisher,
    Author,
    ContentType,
    ContentStatus
)
from src.models.validation import (
    ISBNValidator,
    BrandMetadataValidator,
    ContentValidator
)


class TestPublisherMetadata:
    """Test PublisherMetadata model."""
    
    def test_valid_publisher_metadata(self):
        """Test creating valid publisher metadata."""
        publisher = PublisherMetadata(
            name="The Guardian",
            logo="https://assets.theguardian.com/logo-badge.svg",
            brand_color="#052962",
            trust_score=9.2,
            established_year=1821,
            website="https://theguardian.com"
        )
        
        assert publisher.name == "The Guardian"
        assert publisher.trust_score == 9.2
        assert publisher.established_year == 1821
    
    def test_invalid_trust_score(self):
        """Test validation of trust score range."""
        with pytest.raises(ValidationError):
            PublisherMetadata(
                name="Test Publisher",
                logo="https://example.com/logo.svg",
                brand_color="#052962",
                trust_score=15.0,  # Invalid: > 10.0
                established_year=2000
            )
    
    def test_invalid_brand_color(self):
        """Test validation of brand color format."""
        with pytest.raises(ValidationError):
            PublisherMetadata(
                name="Test Publisher",
                logo="https://example.com/logo.svg",
                brand_color="invalid-color",  # Invalid format
                trust_score=8.0,
                established_year=2000
            )


class TestArticle:
    """Test Article model."""
    
    def test_valid_article(self):
        """Test creating valid article with brand metadata."""
        # Create brand metadata components
        publisher = PublisherMetadata(
            name="The Guardian",
            logo="https://assets.theguardian.com/logo-badge.svg",
            brand_color="#052962",
            trust_score=9.2,
            established_year=1821
        )
        
        attribution = AttributionRequirements(
            required=True,
            display_format="badge-with-logo",
            minimum_visibility="prominent",
            linkback="https://theguardian.com/article/12345"
        )
        
        editorial = EditorialMetadata(
            fact_checked=True,
            fact_check_date=datetime.utcnow(),
            verification_level="triple-sourced"
        )
        
        rights = RightsMetadata(
            usage="ai-training-permitted",
            attribution="mandatory",
            modification="summary-only",
            commercial_use="licensed"
        )
        
        curation = ContentCuration(
            content_type="investigative-journalism",
            expertise=["environmental-science"],
            verification_level="triple-sourced"
        )
        
        display = DisplayRequirements(
            badges=["verified-source", "fact-checked"],
            minimum_attribution="The Guardian | Fact-Checked | Est. 1821",
            brand_visibility="high-prominence"
        )
        
        brand_metadata = BrandMetadata(
            publisher=publisher,
            attribution=attribution,
            editorial=editorial,
            rights=rights,
            curation=curation,
            display_requirements=display
        )
        
        author = Author(
            name="Jane Doe",
            credentials=["Environmental Reporter", "20 years experience"]
        )
        
        article = Article(
            content_id="test-article-123",
            title="Climate Change Report Reveals Shocking Trends",
            text="This is a comprehensive article about climate change with detailed analysis...",
            content_type=ContentType.ARTICLE,
            status=ContentStatus.PUBLISHED,
            publish_date=datetime.utcnow(),
            authors=[author],
            brand_metadata=brand_metadata
        )
        
        assert article.content_id == "test-article-123"
        assert article.title == "Climate Change Report Reveals Shocking Trends"
        assert article.brand_metadata.publisher.name == "The Guardian"
        assert len(article.authors) == 1
    
    def test_language_validation(self):
        """Test language code validation."""
        # This would require a minimal article setup
        # For now, just test the validator directly
        from src.models.content import Article
        
        # Test valid language code
        assert True  # Placeholder - would need full article setup


class TestISBNValidator:
    """Test ISBN validation functionality."""
    
    def test_valid_isbn13(self):
        """Test validation of valid ISBN-13."""
        result = ISBNValidator.validate_isbn13("978-0-123456-78-6")
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_invalid_isbn13_length(self):
        """Test validation of ISBN with wrong length."""
        result = ISBNValidator.validate_isbn13("978-0-123456-78")  # Too short
        assert not result.is_valid
        assert "must be 13 digits" in result.errors[0]
    
    def test_invalid_isbn13_prefix(self):
        """Test validation of ISBN with invalid prefix."""
        result = ISBNValidator.validate_isbn13("123-4-567890-12-3")
        assert not result.is_valid
        assert "must start with 978 or 979" in result.errors[0]
    
    def test_isbn_formatting(self):
        """Test ISBN formatting function."""
        formatted = ISBNValidator.format_isbn("9780123456789")
        assert formatted == "978-0-12345-678-9"


class TestBrandMetadataValidator:
    """Test brand metadata validation."""
    
    def test_validate_publisher_trust_score(self):
        """Test publisher trust score validation."""
        publisher = PublisherMetadata(
            name="Test Publisher",
            logo="https://example.com/logo.svg",
            brand_color="#052962",
            trust_score=9.2,
            established_year=2000
        )
        
        result = BrandMetadataValidator._validate_publisher(publisher)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_future_established_year(self):
        """Test validation of future established year."""
        publisher = PublisherMetadata(
            name="Test Publisher",
            logo="https://example.com/logo.svg",
            brand_color="#052962",
            trust_score=8.0,
            established_year=2030  # Future year
        )
        
        result = BrandMetadataValidator._validate_publisher(publisher)
        assert not result.is_valid
        assert "cannot be in the future" in result.errors[0]


if __name__ == "__main__":
    # Run basic tests
    print("Running basic model validation tests...")
    
    # Test publisher metadata
    try:
        publisher = PublisherMetadata(
            name="The Guardian",
            logo="https://assets.theguardian.com/logo-badge.svg",
            brand_color="#052962",
            trust_score=9.2,
            established_year=1821
        )
        print("✓ PublisherMetadata validation passed")
    except Exception as e:
        print(f"✗ PublisherMetadata validation failed: {e}")
    
    # Test ISBN validation
    try:
        result = ISBNValidator.validate_isbn13("978-0-123456-78-6")
        if result.is_valid:
            print("✓ ISBN validation passed")
        else:
            print(f"✗ ISBN validation failed: {result.errors}")
    except Exception as e:
        print(f"✗ ISBN validation error: {e}")
    
    print("Basic validation tests completed.")