"""Tests for Google Maps scraper module."""
import pytest
from unittest.mock import MagicMock, patch
from selenium.common.exceptions import NoSuchElementException
from scrapers.google_maps import scrape

@pytest.fixture
def mock_driver():
    """Create a mock Selenium WebDriver."""
    driver = MagicMock()
    
    # Mock search box element
    search_box = MagicMock()
    driver.find_element.return_value = search_box
    
    # Mock results
    result1 = MagicMock()
    result1.text = "Test Business 1"
    result2 = MagicMock()
    result2.text = "Test Business 2"
    
    driver.find_elements.return_value = [result1, result2]
    
    # Mock element attributes
    def mock_find_element(*args, **kwargs):
        elem = MagicMock()
        if 'title' in str(args):
            elem.text = "Test Business"
        elif 'phone' in str(args):
            elem.get_attribute.return_value = "123-456-7890"
        elif 'website' in str(args):
            elem.get_attribute.return_value = "https://example.com"
        elif 'address' in str(args):
            elem.text = "123 Test St"
        elif 'rating' in str(args):
            elem.text = "4.5"
        return elem
    
    driver.find_element.side_effect = mock_find_element
    return driver

@patch('scrapers.google_maps.setup_chrome_driver')
def test_scrape_basic_functionality(mock_setup_driver, mock_driver):
    """Test that scrape function returns expected lead format."""
    mock_setup_driver.return_value = mock_driver
    
    results = scrape("cafe", "test city", max_pages=1)
    
    assert len(results) > 0
    assert all(isinstance(lead, dict) for lead in results)
    
    # Check required fields exist
    required_fields = {'business_name', 'phone', 'website', 'address', 'rating', 'notes'}
    assert all(required_fields.issubset(lead.keys()) for lead in results)

@patch('scrapers.google_maps.setup_chrome_driver')
def test_scrape_handles_missing_data(mock_setup_driver, mock_driver):
    """Test that scrape function handles missing elements gracefully."""
    mock_setup_driver.return_value = mock_driver
    
    # Make find_element raise NoSuchElementException for some fields
    def mock_find_element_missing(*args, **kwargs):
        if 'phone' in str(args) or 'website' in str(args):
            raise NoSuchElementException()
        elem = MagicMock()
        elem.text = "Test Data"
        return elem
    
    mock_driver.find_element.side_effect = mock_find_element_missing
    
    results = scrape("cafe", "test city", max_pages=1)
    
    assert len(results) > 0
    # Check that missing fields are empty strings
    assert any(lead['phone'] == "" for lead in results)
    assert any(lead['website'] == "" for lead in results)

@patch('scrapers.google_maps.setup_chrome_driver')
def test_scrape_respects_max_pages(mock_setup_driver, mock_driver):
    """Test that scrape function respects max_pages parameter."""
    mock_setup_driver.return_value = mock_driver
    
    max_pages = 2
    scrape("cafe", "test city", max_pages=max_pages)
    
    # Count number of times find_elements was called (once per page)
    find_elements_calls = mock_driver.find_elements.call_count
    assert find_elements_calls <= max_pages