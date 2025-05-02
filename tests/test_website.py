"""Tests for website scraper module."""
import pytest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from scrapers.website import (
    extract_emails,
    extract_social_links,
    detect_technologies,
    scrape_website,
    enrich
)

@pytest.fixture
def sample_html():
    """Sample HTML content for testing."""
    return """
    <html>
        <body>
            <p>Contact us at test@example.com or support@example.com</p>
            <a href="mailto:info@example.com">Email Us</a>
            <div class="social">
                <a href="https://instagram.com/testbusiness">Instagram</a>
                <a href="https://facebook.com/testbusiness">Facebook</a>
                <a href="https://linkedin.com/company/testbusiness">LinkedIn</a>
            </div>
            <div class="wp-content">WordPress content here</div>
        </body>
    </html>
    """

@pytest.fixture
def sample_leads():
    """Sample leads data for testing enrichment."""
    return [
        {
            "business_name": "Test Business 1",
            "website": "http://example1.com",
            "phone": "123-456-7890"
        },
        {
            "business_name": "Test Business 2",
            "website": "",  # No website
            "phone": "098-765-4321"
        }
    ]

def test_extract_emails():
    """Test email extraction from text."""
    text = "Contact test@example.com or support@test.com or invalid@email"
    emails = extract_emails(text)
    assert len(emails) == 2
    assert "test@example.com" in emails
    assert "support@test.com" in emails
    assert "invalid@email" not in emails

def test_extract_social_links(sample_html):
    """Test social media link extraction."""
    soup = BeautifulSoup(sample_html, 'html.parser')
    social_links = extract_social_links(soup, "https://example.com")
    
    assert len(social_links) == 3
    assert social_links['instagram'] == "https://instagram.com/testbusiness"
    assert social_links['facebook'] == "https://facebook.com/testbusiness"
    assert social_links['linkedin'] == "https://linkedin.com/company/testbusiness"

def test_detect_technologies(sample_html):
    """Test technology detection from HTML."""
    technologies = detect_technologies(sample_html)
    assert "wordpress" in technologies
    assert len(technologies) == 1

@patch('requests.get')
def test_scrape_website(mock_get, sample_html):
    """Test website scraping with mocked response."""
    mock_response = MagicMock()
    mock_response.text = sample_html
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    result = scrape_website("https://example.com")
    
    assert len(result['emails']) == 3
    assert "test@example.com" in result['emails']
    assert len(result['social_links']) == 3
    assert len(result['technologies']) == 1

def test_scrape_website_invalid_url():
    """Test website scraping with invalid URL."""
    result = scrape_website("")
    assert result['emails'] == set()
    assert result['social_links'] == {}
    assert result['technologies'] == []

@patch('scrapers.website.scrape_website')
def test_enrich_leads(mock_scrape, sample_leads):
    """Test lead enrichment process."""
    mock_scrape.return_value = {
        'emails': {'test@example.com'},
        'social_links': {'instagram': 'https://instagram.com/test'},
        'technologies': ['wordpress']
    }
    
    enriched_leads = enrich(sample_leads)
    
    # Test lead with website
    lead1 = enriched_leads[0]
    assert len(lead1['emails']) == 1
    assert 'instagram' in lead1['social_links']
    assert 'wordpress' in lead1['technologies']
    assert 'Technologies' in lead1['notes']
    
    # Test lead without website
    lead2 = enriched_leads[1]
    assert lead2['emails'] == []
    assert lead2['social_links'] == {}
    assert lead2['notes'] == 'No website available'