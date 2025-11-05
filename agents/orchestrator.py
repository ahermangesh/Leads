"""Workflow orchestrator for human-in-the-loop AI agent outreach."""
import json
import time
from typing import Dict, List, Optional, Callable
from datetime import datetime
from utils.logger import setup_logger
try:
    from agents.lead_agent import LeadOutreachAgent
except ImportError:
    # Fallback to simplified agent if LangChain has import issues
    from agents.simple_agent import SimpleLeadAgent as LeadOutreachAgent
from outreach.email_sender import email_sender
from outreach.notion_crm import notion_crm
import yaml

logger = setup_logger(__name__)

class OutreachOrchestrator:
    """Orchestrates the complete lead outreach workflow with human oversight."""
    
    def __init__(
        self,
        on_status_update: Optional[Callable] = None,
        on_lead_update: Optional[Callable] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            on_status_update: Callback for status messages
            on_lead_update: Callback when lead is updated
        """
        self.on_status_update = on_status_update
        self.on_lead_update = on_lead_update
        
        # Initialize AI agent
        self.agent = LeadOutreachAgent(
            on_lead_processed=self._on_lead_processed,
            on_status_update=self._on_status_update
        )
        
        # Load config
        self.config = self._load_config()
        
        # Workflow state
        self.current_batch = []
        self.workflow_stats = {
            'total_leads': 0,
            'researched': 0,
            'qualified': 0,
            'emails_generated': 0,
            'awaiting_approval': 0,
            'approved': 0,
            'rejected': 0,
            'sent': 0,
            'synced_to_notion': 0
        }
        
        logger.info("OutreachOrchestrator initialized")
    
    def _load_config(self) -> dict:
        """Load configuration."""
        try:
            with open("config.yaml", "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _on_status_update(self, message: str):
        """Handle status update from agent."""
        logger.info(message)
        if self.on_status_update:
            self.on_status_update(message)
    
    def _on_lead_processed(self, lead: Dict):
        """Handle processed lead from agent."""
        if self.on_lead_update:
            self.on_lead_update(lead)
    
    def load_leads_from_json(self, json_file_path: str) -> List[Dict]:
        """
        Load leads from a JSON file.
        
        Args:
            json_file_path: Path to JSON file
            
        Returns:
            List of lead dictionaries
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                leads = json.load(f)
            
            logger.info(f"Loaded {len(leads)} leads from {json_file_path}")
            return leads
        except Exception as e:
            logger.error(f"Failed to load leads from JSON: {e}")
            return []
    
    def run_research_phase(
        self,
        leads: List[Dict],
        find_emails: bool = True
    ) -> List[Dict]:
        """
        Run the research phase on all leads.
        
        Args:
            leads: List of lead dictionaries
            find_emails: Whether to find email addresses
            
        Returns:
            Researched leads
        """
        self._on_status_update(f"Starting research phase for {len(leads)} leads...")
        
        result = self.agent.process_batch(
            leads,
            find_email=find_emails,
            do_research=True,
            generate_email=False,  # Don't generate emails yet
            sync_to_notion=False  # Don't sync yet
        )
        
        researched_leads = result['leads']
        stats = result['stats']
        
        self.workflow_stats['total_leads'] = len(researched_leads)
        self.workflow_stats['researched'] = stats['processed']
        self.workflow_stats['qualified'] = stats['qualified']
        
        self._on_status_update(
            f"Research phase complete: {stats['qualified']}/{len(leads)} qualified"
        )
        
        return researched_leads
    
    def run_email_generation_phase(
        self,
        leads: List[Dict],
        min_quality_score: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate emails for qualified leads.
        
        Args:
            leads: List of researched leads
            min_quality_score: Minimum score to generate emails (or None for config default)
            
        Returns:
            Leads with generated emails
        """
        if min_quality_score is None:
            min_quality_score = self.config.get('ai_agent', {}).get('qualification', {}).get('min_score', 60)
        
        # Filter qualified leads
        qualified_leads = [
            lead for lead in leads
            if lead.get('quality_score', 0) >= min_quality_score
        ]
        
        self._on_status_update(
            f"Generating emails for {len(qualified_leads)} qualified leads..."
        )
        
        # Generate emails
        result = self.agent.process_batch(
            qualified_leads,
            find_email=False,  # Already done
            do_research=False,  # Already done
            generate_email=True,
            sync_to_notion=False  # Don't sync yet
        )
        
        generated_leads = result['leads']
        stats = result['stats']
        
        self.workflow_stats['emails_generated'] = stats['emails_generated']
        self.workflow_stats['awaiting_approval'] = stats['emails_generated']
        
        # Mark remaining leads as not qualified
        not_qualified = [
            lead for lead in leads
            if lead.get('quality_score', 0) < min_quality_score
        ]
        
        for lead in not_qualified:
            lead['status'] = 'Not Qualified'
            lead['email_status'] = 'skipped_low_quality'
        
        all_leads = generated_leads + not_qualified
        
        self._on_status_update(
            f"Email generation complete: {stats['emails_generated']} emails ready for approval"
        )
        
        return all_leads
    
    def get_leads_awaiting_approval(self, leads: List[Dict]) -> List[Dict]:
        """
        Get leads that have generated emails awaiting approval.
        
        Args:
            leads: List of all leads
            
        Returns:
            Leads awaiting approval
        """
        return [
            lead for lead in leads
            if lead.get('email_status') == 'generated' and not lead.get('email_approved', False)
        ]
    
    def approve_lead_email(self, lead: Dict) -> Dict:
        """
        Approve an email for sending.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            Updated lead
        """
        lead['email_approved'] = True
        lead['email_approved_at'] = datetime.now().isoformat()
        
        self.workflow_stats['approved'] += 1
        self.workflow_stats['awaiting_approval'] -= 1
        
        logger.info(f"Approved email for {lead.get('business_name')}")
        
        if self.on_lead_update:
            self.on_lead_update(lead)
        
        return lead
    
    def reject_lead_email(self, lead: Dict, reason: Optional[str] = None) -> Dict:
        """
        Reject an email.
        
        Args:
            lead: Lead dictionary
            reason: Optional rejection reason
            
        Returns:
            Updated lead
        """
        lead['email_approved'] = False
        lead['email_rejected'] = True
        lead['email_rejected_at'] = datetime.now().isoformat()
        if reason:
            lead['rejection_reason'] = reason
        
        self.workflow_stats['rejected'] += 1
        self.workflow_stats['awaiting_approval'] -= 1
        
        logger.info(f"Rejected email for {lead.get('business_name')}: {reason}")
        
        if self.on_lead_update:
            self.on_lead_update(lead)
        
        return lead
    
    def bulk_approve(self, leads: List[Dict], criteria: Optional[Dict] = None) -> List[Dict]:
        """
        Bulk approve leads based on criteria.
        
        Args:
            leads: List of leads
            criteria: Optional criteria dict (e.g., {'min_quality_score': 80})
            
        Returns:
            Updated leads
        """
        if criteria is None:
            criteria = {}
        
        min_score = criteria.get('min_quality_score', 70)
        
        approved_count = 0
        for lead in leads:
            if (lead.get('email_status') == 'generated' and 
                not lead.get('email_approved', False) and
                lead.get('quality_score', 0) >= min_score):
                
                self.approve_lead_email(lead)
                approved_count += 1
        
        self._on_status_update(f"Bulk approved {approved_count} leads")
        
        return leads
    
    def run_sending_phase(
        self,
        leads: List[Dict],
        send_approved_only: bool = True
    ) -> Dict:
        """
        Send emails for approved leads.
        
        Args:
            leads: List of leads with generated emails
            send_approved_only: Only send approved emails
            
        Returns:
            Sending statistics
        """
        if not email_sender.is_configured():
            self._on_status_update("Email sender not configured, skipping send phase")
            return {'success': 0, 'failed': 0, 'skipped': len(leads)}
        
        # Filter leads to send
        leads_to_send = leads
        if send_approved_only:
            leads_to_send = [
                lead for lead in leads
                if lead.get('email_approved', False) and lead.get('email_status') == 'generated'
            ]
        
        self._on_status_update(f"Sending {len(leads_to_send)} emails...")
        
        # Send emails
        send_stats = email_sender.send_batch(
            leads_to_send,
            require_approval=send_approved_only
        )
        
        self.workflow_stats['sent'] = send_stats['success']
        
        self._on_status_update(
            f"Sending complete: {send_stats['success']} sent, {send_stats['failed']} failed, {send_stats['skipped']} skipped"
        )
        
        return send_stats
    
    def sync_to_notion(self, leads: List[Dict]) -> Dict:
        """
        Sync all leads to Notion CRM.
        
        Args:
            leads: List of leads to sync
            
        Returns:
            Sync statistics
        """
        if not notion_crm.is_configured():
            self._on_status_update("Notion not configured, skipping sync")
            return {'success': 0, 'failed': 0}
        
        self._on_status_update(f"Syncing {len(leads)} leads to Notion...")
        
        success = 0
        failed = 0
        
        for lead in leads:
            # Skip if already synced
            if lead.get('notion_page_id'):
                continue
            
            try:
                page_id = notion_crm.create_lead_entry(lead)
                if page_id:
                    lead['notion_page_id'] = page_id
                    success += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to sync {lead.get('business_name')}: {e}")
                failed += 1
        
        self.workflow_stats['synced_to_notion'] = success
        
        self._on_status_update(f"Notion sync complete: {success} synced, {failed} failed")
        
        return {'success': success, 'failed': failed}
    
    def run_complete_workflow(
        self,
        json_file_path: str,
        auto_approve_threshold: Optional[int] = None,
        send_emails: bool = False
    ) -> Dict:
        """
        Run the complete workflow from start to finish.
        
        Args:
            json_file_path: Path to JSON file with leads
            auto_approve_threshold: Auto-approve leads above this quality score
            send_emails: Whether to actually send emails (requires manual approval if False)
            
        Returns:
            Complete workflow results
        """
        self._on_status_update("=" * 50)
        self._on_status_update("Starting Complete Outreach Workflow")
        self._on_status_update("=" * 50)
        
        # Phase 1: Load leads
        leads = self.load_leads_from_json(json_file_path)
        if not leads:
            self._on_status_update("No leads loaded, aborting workflow")
            return {'error': 'No leads loaded'}
        
        # Phase 2: Research
        leads = self.run_research_phase(leads, find_emails=True)
        
        # Phase 3: Generate emails
        leads = self.run_email_generation_phase(leads)
        
        # Phase 4: Auto-approve if threshold set
        if auto_approve_threshold:
            leads = self.bulk_approve(leads, {'min_quality_score': auto_approve_threshold})
        
        # Phase 5: Send emails (if enabled and approved)
        send_stats = None
        if send_emails:
            send_stats = self.run_sending_phase(leads, send_approved_only=True)
        else:
            self._on_status_update("Email sending disabled - awaiting manual approval")
        
        # Phase 6: Sync to Notion
        notion_stats = self.sync_to_notion(leads)
        
        # Final summary
        self._on_status_update("=" * 50)
        self._on_status_update("Workflow Complete!")
        self._on_status_update(f"Total Leads: {self.workflow_stats['total_leads']}")
        self._on_status_update(f"Researched: {self.workflow_stats['researched']}")
        self._on_status_update(f"Qualified: {self.workflow_stats['qualified']}")
        self._on_status_update(f"Emails Generated: {self.workflow_stats['emails_generated']}")
        self._on_status_update(f"Approved: {self.workflow_stats['approved']}")
        self._on_status_update(f"Sent: {self.workflow_stats['sent']}")
        self._on_status_update(f"Synced to Notion: {self.workflow_stats['synced_to_notion']}")
        self._on_status_update("=" * 50)
        
        return {
            'leads': leads,
            'stats': self.workflow_stats,
            'send_stats': send_stats,
            'notion_stats': notion_stats
        }
    
    def get_workflow_summary(self) -> str:
        """
        Get a formatted summary of the workflow progress.
        
        Returns:
            Formatted summary string
        """
        summary = f"""
Workflow Summary:
-----------------
Total Leads: {self.workflow_stats['total_leads']}
Researched: {self.workflow_stats['researched']}
Qualified: {self.workflow_stats['qualified']}
Emails Generated: {self.workflow_stats['emails_generated']}
Awaiting Approval: {self.workflow_stats['awaiting_approval']}
Approved: {self.workflow_stats['approved']}
Rejected: {self.workflow_stats['rejected']}
Sent: {self.workflow_stats['sent']}
Synced to Notion: {self.workflow_stats['synced_to_notion']}
"""
        return summary

if __name__ == "__main__":
    # Test orchestrator
    import sys
    
    print("Testing Outreach Orchestrator...")
    
    try:
        orchestrator = OutreachOrchestrator(
            on_status_update=lambda msg: print(f"[STATUS] {msg}")
        )
        
        print("✓ Orchestrator initialized successfully")
        
        if len(sys.argv) > 1:
            json_file = sys.argv[1]
            print(f"\nRunning workflow on {json_file}...")
            
            result = orchestrator.run_complete_workflow(
                json_file,
                auto_approve_threshold=None,  # Manual approval
                send_emails=False  # Don't send in test
            )
            
            print("\n" + orchestrator.get_workflow_summary())
        else:
            print("\nUsage: python orchestrator.py <leads_json_file>")
            print("✓ Orchestrator ready to process leads")
        
    except Exception as e:
        print(f"✗ Failed to initialize orchestrator: {e}")
        import traceback
        traceback.print_exc()

