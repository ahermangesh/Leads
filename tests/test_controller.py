"""Tests for the main controller module."""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from controllers.main_controller import LeadController

@pytest.fixture
def controller():
    """Create a LeadController instance for testing."""
    return LeadController()

@pytest.fixture
def sample_leads():
    """Create sample lead data for testing."""
    return [
        {
            "business_name": "Test Cafe 1",
            "phone": "123-456-7890",
            "website": "https://test1.com",
            "address": "123 Test St",
            "rating": "4.5"
        },
        {
            "business_name": "Test Cafe 2",
            "phone": "098-765-4321",
            "website": "https://test2.com",
            "address": "456 Test Ave",
            "rating": "4.0"
        }
    ]

def test_input_validation(controller):
    """Test input validation for the controller."""
    # Test empty keyword
    with pytest.raises(ValueError, match="Business type cannot be empty"):
        controller.validate_inputs("", "New York")
    
    # Test empty location
    with pytest.raises(ValueError, match="Location cannot be empty"):
        controller.validate_inputs("Cafe", "")
    
    # Test whitespace-only inputs
    with pytest.raises(ValueError, match="Business type cannot be empty"):
        controller.validate_inputs("  ", "New York")
    
    # Test valid inputs
    controller.validate_inputs("Cafe", "New York")  # Should not raise

@patch('controllers.main_controller.scrape_maps')
@patch('controllers.main_controller.enrich_leads')
def test_run_google_maps_only(mock_enrich, mock_scrape_maps, controller, sample_leads):
    """Test running controller with Google Maps platform only."""
    mock_scrape_maps.return_value = sample_leads
    
    result = controller.run(
        "Cafe",
        "New York",
        platforms=["Google Maps"],
        mode="Contacts Only"
    )
    
    assert mock_scrape_maps.called
    assert not mock_enrich.called
    assert len(result['leads']) == len(sample_leads)
    assert 'export_paths' in result

@patch('controllers.main_controller.scrape_maps')
@patch('controllers.main_controller.enrich_leads')
def test_run_full_data_mode(mock_enrich, mock_scrape_maps, controller, sample_leads):
    """Test running controller in Full Data mode."""
    mock_scrape_maps.return_value = sample_leads
    enriched_leads = sample_leads.copy()
    for lead in enriched_leads:
        lead.update({
            'emails': ['test@example.com'],
            'social_links': {'instagram': 'https://instagram.com/test'},
            'technologies': ['wordpress']
        })
    mock_enrich.return_value = enriched_leads
    
    result = controller.run(
        "Cafe",
        "New York",
        platforms=["Google Maps", "Website Scraper"],
        mode="Full Data"
    )
    
    assert mock_scrape_maps.called
    assert mock_enrich.called
    assert len(result['leads']) == len(enriched_leads)
    assert 'emails' in result['leads'][0]
    assert 'export_paths' in result

@patch('pandas.DataFrame.to_csv')
@patch('pandas.DataFrame.to_excel')
def test_export_data(mock_to_excel, mock_to_csv, controller, sample_leads):
    """Test data export functionality."""
    export_paths = controller.export_data(sample_leads, "Cafe", "New York")
    
    assert mock_to_csv.called
    assert mock_to_excel.called
    assert 'csv' in export_paths
    assert 'xlsx' in export_paths
    assert export_paths['csv'].endswith('.csv')
    assert export_paths['xlsx'].endswith('.xlsx')