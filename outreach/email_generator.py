"""AI-powered email generation system using Gemini."""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yaml
from utils.logger import setup_logger
from utils.ai_helpers import generate_text
import os
from dotenv import load_dotenv

logger = setup_logger(__name__)
load_dotenv()

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def get_email_config() -> dict:
    """Get email configuration settings."""
    config = load_config()
    return config.get('ai_agent', {}).get('email', {})

def get_unsubscribe_link() -> str:
    """Get unsubscribe link for CAN-SPAM compliance."""
    # In production, this should be a real unsubscribe endpoint
    sender_email = os.getenv('SENDER_EMAIL', 'your@email.com')
    return f"mailto:{sender_email}?subject=Unsubscribe"

def generate_subject_line(
    lead: Dict,
    strategy: str = "value_proposition",
    tone: str = "professional"
) -> str:
    """
    Generate personalized email subject line using AI.
    
    Args:
        lead: Lead dictionary with business info and research
        strategy: Email strategy (value_proposition, pain_point, social_proof)
        tone: Email tone (professional, casual, friendly, formal)
        
    Returns:
        Generated subject line
    """
    business_name = lead.get('business_name', 'there')
    industry = lead.get('industry', lead.get('business_summary', 'your business'))
    
    # Build context for AI
    context = f"""Business: {business_name}
Industry: {industry}"""
    
    if lead.get('pain_points'):
        context += f"\nPain Points: {', '.join(lead['pain_points'][:2])}"
    
    if lead.get('target_audience'):
        context += f"\nTarget Audience: {lead['target_audience']}"
    
    # Create strategy-specific prompt
    strategy_prompts = {
        "value_proposition": "Create a subject line that highlights the value we can bring to their business.",
        "pain_point": "Create a subject line that addresses a specific pain point they might be facing.",
        "social_proof": "Create a subject line that mentions success with similar businesses."
    }
    
    strategy_instruction = strategy_prompts.get(strategy, strategy_prompts["value_proposition"])
    
    prompt = f"""Write a compelling email subject line for outreach to this business.

{context}

Tone: {tone}
Strategy: {strategy_instruction}

Requirements:
- Maximum 60 characters
- Personalized to their business
- Intriguing and relevant
- No spam words (FREE, URGENT, etc.)
- Professional and respectful

Return ONLY the subject line, nothing else."""
    
    try:
        subject = generate_text(prompt)
        
        if subject:
            # Clean up the response
            subject = subject.strip().strip('"').strip("'")
            
            # Ensure it's not too long
            config = get_email_config()
            max_length = config.get('max_subject_length', 60)
            if len(subject) > max_length:
                subject = subject[:max_length-3] + "..."
            
            logger.info(f"Generated subject line for {business_name}: {subject}")
            return subject
        else:
            # Fallback subject
            return f"Quick question for {business_name}"
            
    except Exception as e:
        logger.error(f"Error generating subject line: {str(e)}")
        return f"Reaching out to {business_name}"

def generate_email_body(
    lead: Dict,
    strategy: str = "value_proposition",
    tone: str = "professional",
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None
) -> str:
    """
    Generate personalized email body using AI.
    
    Args:
        lead: Lead dictionary with business info and research
        strategy: Email strategy
        tone: Email tone
        sender_name: Name of sender
        sender_company: Sender's company name
        
    Returns:
        Generated email body
    """
    business_name = lead.get('business_name', 'there')
    
    if not sender_name:
        sender_name = os.getenv('SENDER_NAME', 'Your Name')
    
    # Build comprehensive context
    context = f"""Business Name: {business_name}
Website: {lead.get('website', 'N/A')}"""
    
    if lead.get('business_summary'):
        context += f"\nWhat they do: {lead['business_summary']}"
    
    if lead.get('industry'):
        context += f"\nIndustry: {lead['industry']}"
    
    if lead.get('target_audience'):
        context += f"\nTheir target audience: {lead['target_audience']}"
    
    if lead.get('pain_points'):
        context += f"\nPotential challenges: {', '.join(lead['pain_points'][:3])}"
    
    if lead.get('outreach_angles'):
        context += f"\nSuggested angles: {', '.join(lead['outreach_angles'][:2])}"
    
    # Strategy-specific instructions
    strategy_instructions = {
        "value_proposition": """Focus on the value and benefits you can provide. 
Mention specific results or improvements they could see.
Make it about solving their problems, not about your services.""",
        
        "pain_point": """Address a specific pain point they likely face in their industry.
Show empathy and understanding of their challenges.
Offer a solution without being too sales-y.""",
        
        "social_proof": """Mention brief success with similar businesses (without naming them).
Use specific metrics or results when possible.
Build credibility through results."""
    }
    
    strategy_instruction = strategy_instructions.get(strategy, strategy_instructions["value_proposition"])
    
    # Get config settings
    config = get_email_config()
    max_length = config.get('max_body_length', 500)
    include_unsubscribe = config.get('include_unsubscribe', True)
    
    # Create AI prompt
    prompt = f"""Write a personalized cold outreach email to this business.

BUSINESS CONTEXT:
{context}

YOUR INFO:
Sender: {sender_name}
{f'Company: {sender_company}' if sender_company else ''}

REQUIREMENTS:
- Tone: {tone}
- Strategy: {strategy_instruction}
- Maximum {max_length} words
- Personalize based on their business
- Start with a personalized greeting
- Show you've researched them
- Clear but soft call-to-action
- Professional and respectful
- No generic templates
- No excessive flattery
- Keep it concise and scannable

STRUCTURE:
1. Personalized opening (show you know their business)
2. Brief value proposition or pain point
3. Soft call-to-action
4. Professional closing

Write ONLY the email body (no subject line). Use their business name naturally."""
    
    try:
        body = generate_text(prompt)
        
        if body:
            # Clean up the response
            body = body.strip()
            
            # Add signature
            signature = f"\n\nBest regards,\n{sender_name}"
            if sender_company:
                signature += f"\n{sender_company}"
            
            body += signature
            
            # Add unsubscribe link if required (CAN-SPAM compliance)
            if include_unsubscribe:
                unsubscribe_link = get_unsubscribe_link()
                body += f"\n\n---\nTo unsubscribe, click here: {unsubscribe_link}"
            
            logger.info(f"Generated email body for {business_name} ({len(body)} chars)")
            return body
        else:
            # Fallback email
            return generate_fallback_email(lead, sender_name, sender_company)
            
    except Exception as e:
        logger.error(f"Error generating email body: {str(e)}")
        return generate_fallback_email(lead, sender_name, sender_company)

def generate_fallback_email(
    lead: Dict,
    sender_name: str,
    sender_company: Optional[str] = None
) -> str:
    """Generate a simple fallback email when AI fails."""
    business_name = lead.get('business_name', 'there')
    
    email = f"""Hi {business_name} team,

I came across your business and was impressed by what you're doing.

I wanted to reach out to see if you'd be interested in connecting to discuss how we might be able to help you grow your business.

Would you be open to a quick conversation?

Best regards,
{sender_name}"""
    
    if sender_company:
        email += f"\n{sender_company}"
    
    config = get_email_config()
    if config.get('include_unsubscribe', True):
        email += f"\n\n---\nTo unsubscribe, click here: {get_unsubscribe_link()}"
    
    return email

def generate_complete_email(
    lead: Dict,
    strategy: Optional[str] = None,
    tone: Optional[str] = None,
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate complete email with subject and body.
    
    Args:
        lead: Lead dictionary
        strategy: Email strategy (or None to use config default)
        tone: Email tone (or None to use config default)
        sender_name: Sender name (or None to use env variable)
        sender_company: Sender company
        
    Returns:
        Dictionary with 'subject' and 'body' keys
    """
    config = get_email_config()
    
    # Use config defaults if not provided
    if not tone:
        tone = config.get('tone', 'professional')
    
    if not strategy:
        strategies = config.get('strategies', ['value_proposition'])
        strategy = strategies[0] if strategies else 'value_proposition'
    
    if not sender_name:
        sender_name = os.getenv('SENDER_NAME', 'Your Name')
    
    logger.info(f"Generating email for {lead.get('business_name')} using {strategy} strategy with {tone} tone")
    
    # Generate subject and body
    subject = generate_subject_line(lead, strategy, tone)
    body = generate_email_body(lead, strategy, tone, sender_name, sender_company)
    
    return {
        'subject': subject,
        'body': body,
        'strategy': strategy,
        'tone': tone,
        'generated_at': datetime.now().isoformat()
    }

def batch_generate_emails(
    leads: List[Dict],
    strategy: Optional[str] = None,
    tone: Optional[str] = None,
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None
) -> List[Dict]:
    """
    Generate emails for multiple leads.
    
    Args:
        leads: List of lead dictionaries
        strategy: Email strategy
        tone: Email tone
        sender_name: Sender name
        sender_company: Sender company
        
    Returns:
        List of leads with email data added
    """
    logger.info(f"Generating emails for {len(leads)} leads")
    
    for i, lead in enumerate(leads):
        try:
            logger.info(f"Generating email {i+1}/{len(leads)} for {lead.get('business_name')}")
            
            email_data = generate_complete_email(
                lead,
                strategy=strategy,
                tone=tone,
                sender_name=sender_name,
                sender_company=sender_company
            )
            
            # Add email data to lead
            lead['email_subject'] = email_data['subject']
            lead['email_body'] = email_data['body']
            lead['email_strategy'] = email_data['strategy']
            lead['email_tone'] = email_data['tone']
            lead['email_generated_at'] = email_data['generated_at']
            lead['email_status'] = 'generated'
            
        except Exception as e:
            logger.error(f"Error generating email for {lead.get('business_name')}: {str(e)}")
            lead['email_status'] = 'generation_failed'
            lead['email_error'] = str(e)
    
    successful = sum(1 for lead in leads if lead.get('email_status') == 'generated')
    logger.info(f"Generated {successful}/{len(leads)} emails successfully")
    
    return leads

def regenerate_email_with_feedback(
    lead: Dict,
    previous_subject: str,
    previous_body: str,
    feedback: str,
    sender_name: Optional[str] = None,
    sender_company: Optional[str] = None
) -> Dict[str, str]:
    """
    Regenerate email based on user feedback.
    
    Args:
        lead: Lead dictionary
        previous_subject: Previous subject line
        previous_body: Previous email body
        feedback: User feedback on what to change
        sender_name: Sender name
        sender_company: Sender company
        
    Returns:
        Dictionary with new 'subject' and 'body'
    """
    business_name = lead.get('business_name', 'there')
    
    if not sender_name:
        sender_name = os.getenv('SENDER_NAME', 'Your Name')
    
    prompt = f"""Improve this email based on user feedback.

Business: {business_name}

PREVIOUS EMAIL:
Subject: {previous_subject}

Body:
{previous_body}

USER FEEDBACK: {feedback}

Please rewrite the email incorporating the feedback. Return in this format:
SUBJECT: [new subject line]

BODY:
[new email body]"""
    
    try:
        response = generate_text(prompt)
        
        if response:
            # Parse response
            lines = response.split('\n')
            subject = previous_subject
            body_lines = []
            in_body = False
            
            for line in lines:
                if line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                elif line.startswith('BODY:'):
                    in_body = True
                elif in_body:
                    body_lines.append(line)
            
            body = '\n'.join(body_lines).strip()
            
            if not body:
                body = response  # Fallback to full response
            
            # Add signature if not present
            if sender_name not in body:
                body += f"\n\nBest regards,\n{sender_name}"
                if sender_company:
                    body += f"\n{sender_company}"
            
            # Add unsubscribe link
            config = get_email_config()
            if config.get('include_unsubscribe', True) and 'unsubscribe' not in body.lower():
                body += f"\n\n---\nTo unsubscribe, click here: {get_unsubscribe_link()}"
            
            return {
                'subject': subject,
                'body': body,
                'regenerated_at': datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"Error regenerating email: {str(e)}")
    
    # Return original if regeneration fails
    return {
        'subject': previous_subject,
        'body': previous_body
    }

if __name__ == "__main__":
    # Test email generator
    import sys
    import json
    
    if len(sys.argv) > 1:
        # Test with a JSON file of leads
        with open(sys.argv[1], 'r') as f:
            leads = json.load(f)
        
        if leads:
            test_lead = leads[0]
            print(f"\nTesting email generator for: {test_lead.get('business_name')}")
            
            email = generate_complete_email(test_lead)
            
            print(f"\nSubject: {email['subject']}")
            print(f"\nBody:\n{email['body']}")
    else:
        print("Usage: python email_generator.py <leads_json_file>")

