"""Resend email sender with rate limiting and tracking."""
import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import resend
from utils.logger import setup_logger
import yaml

logger = setup_logger(__name__)
load_dotenv()

class EmailSender:
    """Email sender using Resend API with rate limiting and tracking."""
    
    def __init__(self):
        """Initialize Resend client."""
        self.api_key = os.getenv('RESEND_API_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_name = os.getenv('SENDER_NAME', 'Your Name')
        
        if not self.api_key or self.api_key == 'your_resend_api_key_here':
            logger.warning("Resend API key not configured")
            self.configured = False
        else:
            try:
                resend.api_key = self.api_key
                self.configured = True
                logger.info("Resend email sender initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Resend: {e}")
                self.configured = False
        
        # Load configuration
        self.config = self._load_config()
        
        # Rate limiting tracking
        self.emails_sent_today = 0
        self.last_reset_date = datetime.now().date()
        self.last_send_time = None
    
    def _load_config(self) -> dict:
        """Load configuration from config.yaml."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get('ai_agent', {}).get('outreach', {})
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def is_configured(self) -> bool:
        """Check if email sender is properly configured."""
        return (
            self.configured and 
            self.sender_email and 
            self.sender_email != 'your@email.com'
        )
    
    def _reset_daily_counter(self):
        """Reset daily email counter if it's a new day."""
        today = datetime.now().date()
        if today > self.last_reset_date:
            self.emails_sent_today = 0
            self.last_reset_date = today
            logger.info("Reset daily email counter")
    
    def _check_rate_limit(self) -> bool:
        """
        Check if we can send an email based on rate limits.
        
        Returns:
            True if allowed to send, False otherwise
        """
        self._reset_daily_counter()
        
        max_per_day = self.config.get('max_emails_per_day', 50)
        
        if self.emails_sent_today >= max_per_day:
            logger.warning(f"Daily email limit reached ({max_per_day})")
            return False
        
        return True
    
    def _apply_delay(self):
        """Apply delay between emails to respect rate limits."""
        delay = self.config.get('delay_between_emails', 10)
        
        if self.last_send_time:
            elapsed = time.time() - self.last_send_time
            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.info(f"Rate limiting: sleeping for {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        self.last_send_time = time.time()
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        to_name: Optional[str] = None
    ) -> Dict:
        """
        Send a single email using Resend API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            to_name: Optional recipient name
            
        Returns:
            Dictionary with send result
        """
        if not self.is_configured():
            logger.error("Email sender not configured")
            return {
                'success': False,
                'error': 'Email sender not configured',
                'email': to_email
            }
        
        # Check rate limits
        if not self._check_rate_limit():
            return {
                'success': False,
                'error': 'Daily rate limit reached',
                'email': to_email
            }
        
        # Apply delay
        self._apply_delay()
        
        try:
            # Prepare email parameters
            from_address = f"{self.sender_name} <{self.sender_email}>"
            to_address = f"{to_name} <{to_email}>" if to_name else to_email
            
            # Send email
            logger.info(f"Sending email to {to_email}")
            
            response = resend.Emails.send({
                "from": from_address,
                "to": to_address,
                "subject": subject,
                "text": body,
            })
            
            # Update counters
            self.emails_sent_today += 1
            
            logger.info(f"Email sent successfully to {to_email}. ID: {response.get('id')}")
            
            return {
                'success': True,
                'email': to_email,
                'email_id': response.get('id'),
                'sent_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'email': to_email
            }
    
    def send_batch(
        self,
        leads: List[Dict],
        require_approval: bool = True
    ) -> Dict[str, any]:
        """
        Send emails to multiple leads in batch.
        
        Args:
            leads: List of lead dictionaries with email data
            require_approval: Whether to require approval before sending
            
        Returns:
            Dictionary with batch send statistics
        """
        if not self.is_configured():
            logger.error("Email sender not configured")
            return {
                'total': len(leads),
                'success': 0,
                'failed': 0,
                'skipped': len(leads),
                'results': []
            }
        
        stats = {
            'total': len(leads),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'results': []
        }
        
        logger.info(f"Starting batch send for {len(leads)} leads")
        
        for i, lead in enumerate(leads):
            # Check if lead has required fields
            if not lead.get('emails') or not lead['emails']:
                logger.warning(f"No email for {lead.get('business_name')}, skipping")
                stats['skipped'] += 1
                continue
            
            if not lead.get('email_subject') or not lead.get('email_body'):
                logger.warning(f"No generated email for {lead.get('business_name')}, skipping")
                stats['skipped'] += 1
                continue
            
            # Get primary email (first one, usually highest confidence)
            to_email = lead['emails'][0]
            
            # Skip if approval required and not approved
            if require_approval and not lead.get('email_approved', False):
                logger.info(f"Email not approved for {lead.get('business_name')}, skipping")
                stats['skipped'] += 1
                continue
            
            # Send email
            result = self.send_email(
                to_email=to_email,
                subject=lead['email_subject'],
                body=lead['email_body'],
                to_name=lead.get('business_name')
            )
            
            # Update lead with send result
            if result['success']:
                lead['email_sent'] = True
                lead['email_sent_at'] = result['sent_at']
                lead['email_id'] = result.get('email_id')
                lead['status'] = 'Email Sent'
                stats['success'] += 1
            else:
                lead['email_sent'] = False
                lead['email_error'] = result.get('error')
                stats['failed'] += 1
            
            stats['results'].append(result)
            
            logger.info(f"Batch progress: {i+1}/{len(leads)}, Success: {stats['success']}, Failed: {stats['failed']}, Skipped: {stats['skipped']}")
        
        logger.info(f"Batch send completed: {stats['success']} success, {stats['failed']} failed, {stats['skipped']} skipped")
        
        return stats
    
    def get_email_stats(self) -> Dict:
        """
        Get current email sending statistics.
        
        Returns:
            Dictionary with stats
        """
        self._reset_daily_counter()
        
        max_per_day = self.config.get('max_emails_per_day', 50)
        remaining = max_per_day - self.emails_sent_today
        
        return {
            'configured': self.is_configured(),
            'emails_sent_today': self.emails_sent_today,
            'max_per_day': max_per_day,
            'remaining_today': remaining,
            'last_send_time': self.last_send_time,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name
        }
    
    def preview_email(self, lead: Dict) -> str:
        """
        Generate a preview of the email that would be sent.
        
        Args:
            lead: Lead dictionary with email data
            
        Returns:
            Formatted email preview
        """
        to_email = lead.get('emails', ['No email'])[0] if lead.get('emails') else 'No email'
        
        preview = f"""
=== EMAIL PREVIEW ===

From: {self.sender_name} <{self.sender_email}>
To: {lead.get('business_name', 'Unknown')} <{to_email}>
Subject: {lead.get('email_subject', 'No subject')}

---

{lead.get('email_body', 'No body')}

=== END PREVIEW ===
"""
        return preview

# Global instance
email_sender = EmailSender()

def send_single_email(lead: Dict, force: bool = False) -> Dict:
    """
    Convenience function to send email for a single lead.
    
    Args:
        lead: Lead dictionary
        force: Force send even if not approved
        
    Returns:
        Send result dictionary
    """
    if not force and not lead.get('email_approved', False):
        return {
            'success': False,
            'error': 'Email not approved',
            'email': lead.get('emails', [''])[0] if lead.get('emails') else ''
        }
    
    if not lead.get('emails'):
        return {
            'success': False,
            'error': 'No email address',
            'email': ''
        }
    
    return email_sender.send_email(
        to_email=lead['emails'][0],
        subject=lead.get('email_subject', 'Hello'),
        body=lead.get('email_body', ''),
        to_name=lead.get('business_name')
    )

if __name__ == "__main__":
    # Test email sender
    print("Testing Email Sender...")
    
    if email_sender.is_configured():
        print("✓ Email sender is configured")
        
        stats = email_sender.get_email_stats()
        print(f"\nEmail Stats:")
        print(f"  Sender: {stats['sender_name']} <{stats['sender_email']}>")
        print(f"  Sent today: {stats['emails_sent_today']}/{stats['max_per_day']}")
        print(f"  Remaining: {stats['remaining_today']}")
        
        # Test with a sample lead (won't actually send without confirmation)
        test_lead = {
            'business_name': 'Test Business',
            'emails': ['test@example.com'],
            'email_subject': 'Test Subject',
            'email_body': 'This is a test email body.',
            'email_approved': False
        }
        
        preview = email_sender.preview_email(test_lead)
        print(f"\n{preview}")
        
        print("\n(Not sending - test lead not approved)")
        
    else:
        print("✗ Email sender not configured")
        print("Please set RESEND_API_KEY and SENDER_EMAIL in .env file")

