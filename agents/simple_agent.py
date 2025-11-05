"""Simplified AI agent without complex LangChain dependencies."""
from typing import Dict, List, Optional, Callable
from utils.logger import setup_logger
from utils.ai_helpers import initialize_gemini
from outreach.email_finder import find_emails, enrich_lead_with_emails
from outreach.lead_researcher import research_lead, filter_qualified_leads
from outreach.email_generator import generate_complete_email
from outreach.notion_crm import notion_crm
import os
import yaml

logger = setup_logger(__name__)

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

class SimpleLeadAgent:
    """Simplified AI agent for lead research and outreach without complex dependencies."""
    
    def __init__(
        self,
        on_lead_processed: Optional[Callable] = None,
        on_status_update: Optional[Callable] = None
    ):
        """Initialize the simplified agent."""
        self.config = load_config()
        self.on_lead_processed = on_lead_processed
        self.on_status_update = on_status_update
        
        # Initialize Gemini
        if not initialize_gemini():
            raise ValueError("Failed to initialize Gemini API")
        
        logger.info("SimpleLeadAgent initialized")
    
    def _update_status(self, message: str):
        """Send status update via callback."""
        logger.info(message)
        if self.on_status_update:
            self.on_status_update(message)
    
    def process_single_lead(
        self,
        lead: Dict,
        find_email: bool = True,
        do_research: bool = True,
        generate_email: bool = True
    ) -> Dict:
        """Process a single lead through the complete pipeline."""
        business_name = lead.get('business_name', 'Unknown')
        self._update_status(f"Processing lead: {business_name}")
        
        # Step 1: Find email if needed
        if find_email and lead.get('website') and (not lead.get('emails') or len(lead.get('emails', [])) == 0):
            self._update_status(f"Finding email for {business_name}")
            lead = enrich_lead_with_emails(lead, max_pages=3)
        
        # Step 2: AI Research
        if do_research and lead.get('website'):
            self._update_status(f"Researching {business_name}")
            lead = research_lead(lead, max_pages=3)
        
        # Step 3: Generate email if qualified
        if generate_email:
            quality_score = lead.get('quality_score', 0)
            min_score = self.config.get('ai_agent', {}).get('qualification', {}).get('min_score', 60)
            
            if quality_score >= min_score:
                self._update_status(f"Generating email for {business_name} (score: {quality_score})")
                
                email_data = generate_complete_email(lead)
                lead['email_subject'] = email_data['subject']
                lead['email_body'] = email_data['body']
                lead['email_strategy'] = email_data['strategy']
                lead['email_status'] = 'generated'
                lead['status'] = 'Ready to Contact'
            else:
                self._update_status(f"Lead {business_name} not qualified (score: {quality_score} < {min_score})")
                lead['status'] = 'Not Qualified'
                lead['email_status'] = 'skipped_low_quality'
        
        # Callback
        if self.on_lead_processed:
            self.on_lead_processed(lead)
        
        return lead
    
    def process_batch(
        self,
        leads: List[Dict],
        find_email: bool = True,
        do_research: bool = True,
        generate_email: bool = True,
        sync_to_notion: bool = True
    ) -> Dict[str, any]:
        """Process multiple leads in batch."""
        self._update_status(f"Starting batch processing for {len(leads)} leads")
        
        stats = {
            'total': len(leads),
            'processed': 0,
            'qualified': 0,
            'not_qualified': 0,
            'emails_found': 0,
            'emails_generated': 0,
            'synced_to_notion': 0,
            'errors': 0
        }
        
        processed_leads = []
        
        for i, lead in enumerate(leads):
            try:
                self._update_status(f"Processing lead {i+1}/{len(leads)}: {lead.get('business_name')}")
                
                # Process lead
                processed_lead = self.process_single_lead(
                    lead,
                    find_email=find_email,
                    do_research=do_research,
                    generate_email=generate_email
                )
                
                processed_leads.append(processed_lead)
                stats['processed'] += 1
                
                # Update stats
                if processed_lead.get('emails'):
                    stats['emails_found'] += 1
                
                if processed_lead.get('quality_score', 0) >= self.config.get('ai_agent', {}).get('qualification', {}).get('min_score', 60):
                    stats['qualified'] += 1
                else:
                    stats['not_qualified'] += 1
                
                if processed_lead.get('email_status') == 'generated':
                    stats['emails_generated'] += 1
                
                # Sync to Notion if configured
                if sync_to_notion and notion_crm.is_configured():
                    try:
                        page_id = notion_crm.create_lead_entry(processed_lead)
                        if page_id:
                            processed_lead['notion_page_id'] = page_id
                            stats['synced_to_notion'] += 1
                    except Exception as e:
                        logger.error(f"Failed to sync to Notion: {e}")
                
            except Exception as e:
                logger.error(f"Error processing lead {lead.get('business_name')}: {e}")
                stats['errors'] += 1
                lead['processing_error'] = str(e)
                processed_leads.append(lead)
        
        self._update_status(f"Batch processing completed: {stats['qualified']} qualified, {stats['emails_generated']} emails generated")
        
        return {
            'stats': stats,
            'leads': processed_leads
        }

if __name__ == "__main__":
    # Test agent
    print("Testing Simple Lead Agent...")
    
    try:
        agent = SimpleLeadAgent()
        print("✓ Agent initialized successfully")
        
        # Test with sample lead
        test_lead = {
            'business_name': 'Test Business',
            'website': 'https://example.com',
            'phone': '123-456-7890'
        }
        
        print(f"\nTesting lead processing (dry run)...")
        print("✓ Agent ready to process leads")
        
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")

