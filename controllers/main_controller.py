"""Main controller module for Lead Scraper."""
from typing import Dict, List, Optional, Callable
import json
import pandas as pd
from datetime import datetime
from utils.logger import setup_logger
from scrapers.google_maps import scrape as scrape_maps
from scrapers.website import enrich as enrich_leads

logger = setup_logger(__name__)

class LeadController:
    """Coordinates scraping modules and data processing."""
    
    def __init__(self, on_lead_extracted=None, on_log_message=None, max_leads=15):
        """
        Initialize controller.
        
        Args:
            on_lead_extracted: Optional callback function that gets called when a lead is extracted
            on_log_message: Optional callback function that gets called with log messages
            max_leads: Maximum number of leads to collect
        """
        self.logger = logger
        self.on_lead_extracted = on_lead_extracted  # Callback for live data updates
        self.on_log_message = on_log_message  # Callback for log messages
        self.max_leads = max_leads  # Maximum number of leads to collect
    
    def log(self, message: str) -> None:
        """
        Log a message and call the log message callback if defined.
        
        Args:
            message: The message to log
        """
        self.logger.info(message)
        if self.on_log_message:
            self.on_log_message(message)
    
    def validate_inputs(self, keyword: str, location: str) -> None:
        """
        Validate user inputs before starting scraping.
        
        Args:
            keyword: Business type to search for
            location: Location to search in
            
        Raises:
            ValueError: If inputs are empty or invalid
        """
        if not keyword or not keyword.strip():
            raise ValueError("Business type cannot be empty")
        if not location or not location.strip():
            raise ValueError("Location cannot be empty")
    
    def export_data(self, leads: List[Dict], keyword: str, location: str) -> Dict[str, str]:
        """
        Export leads to CSV, XLSX, and JSON files.
        
        Args:
            leads: List of lead dictionaries to export
            keyword: Business type used in search
            location: Location used in search
            
        Returns:
            Dictionary with paths to exported files
        """
        # Convert leads to DataFrame
        df = pd.DataFrame.from_records(leads)
        
        # Generate timestamp and filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"leads_{keyword}_{location}_{timestamp}"
        csv_path = f"data/output/{base_name}.csv"
        xlsx_path = f"data/output/{base_name}.xlsx"
        json_path = f"data/output/{base_name}.json"
        
        # Export to all formats
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)
        
        # Export to JSON with cleaner formatting
        clean_leads = self.clean_leads_for_export(leads)
        with open(json_path, 'w', encoding='utf-8') as json_file:
            json.dump(clean_leads, json_file, indent=2, ensure_ascii=False)
        
        self.log(f"Exported {len(leads)} leads to {csv_path}, {xlsx_path}, and {json_path}")
        
        return {
            'csv': csv_path,
            'xlsx': xlsx_path,
            'json': json_path
        }
    
    def clean_leads_for_export(self, leads: List[Dict]) -> List[Dict]:
        """
        Clean and normalize lead data for export, removing redundancies.
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            Cleaned list of leads for export
        """
        clean_leads = []
        
        for lead in leads:
            clean_lead = {
                'business_name': lead.get('business_name', ''),
                'phone': lead.get('phone', ''),
                'website': lead.get('website', ''),
                'address': lead.get('address', ''),
                'rating': lead.get('rating', '')
            }
            
            # Add emails if present
            if 'emails' in lead and lead['emails']:
                clean_lead['emails'] = lead['emails']
            
            # Add social links if present, converting dict to simpler format
            if 'social_links' in lead and lead['social_links']:
                clean_lead['social_links'] = lead['social_links']
            
            # Add technologies if present
            if 'technologies' in lead and lead['technologies']:
                clean_lead['technologies'] = lead['technologies']
            
            # Add notes if present and not empty
            if 'notes' in lead and lead['notes']:
                clean_lead['notes'] = lead['notes']
            
            clean_leads.append(clean_lead)
        
        return clean_leads
    
    def on_lead_callback(self, lead: Dict) -> None:
        """
        Process a lead as it's extracted and call any registered callbacks.
        
        Args:
            lead: The lead dictionary that was just extracted
        """
        if self.on_lead_extracted:
            self.on_lead_extracted(lead)
    
    def run(
        self, 
        keyword: str, 
        location: str, 
        platforms: List[str], 
        mode: str = "Full Data"
    ) -> Dict:
        """
        Run the scraping pipeline.
        
        Args:
            keyword: Business type to search for
            location: Location to search in
            platforms: List of platforms to scrape from
            mode: Scraping mode (Contacts Only or Full Data)
            
        Returns:
            Dictionary containing leads and export file paths
        """
        self.validate_inputs(keyword, location)
        self.log(f"Starting scraping for {keyword} in {location} (Max leads: {self.max_leads})")
        
        leads: List[Dict] = []
        
        # Google Maps scraping
        if "Google Maps" in platforms:
            self.log("Starting Google Maps scraping")
            leads = scrape_maps(
                keyword, 
                location, 
                max_results=self.max_leads,
                on_lead_callback=self.on_lead_callback
            )
            self.log(f"Found {len(leads)} leads from Google Maps")
        
        # Website scraping for Full Data mode
        if mode == "Full Data" and leads and "Website Scraper" in platforms:
            self.log("Starting website data enrichment")
            leads = enrich_leads(
                leads,
                on_lead_callback=self.on_lead_callback
            )
            self.log("Completed website data enrichment")
        
        # Export data
        export_paths = self.export_data(leads, keyword, location)
        
        return {
            'leads': leads,
            'export_paths': export_paths,
            'keyword': keyword,
            'location': location
        }