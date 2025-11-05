"""Enhanced email finder with multi-page scraping and validation."""
import re
import time
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
import validators
from utils.logger import setup_logger
from utils.decorators import retry_with_backoff
import yaml

logger = setup_logger(__name__)

# Email regex pattern
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Common pages that contain contact information
CONTACT_PAGES = [
    '/',
    '/contact',
    '/contact-us',
    '/contactus',
    '/about',
    '/about-us',
    '/aboutus',
    '/team',
    '/our-team',
    '/leadership',
    '/get-in-touch',
    '/reach-us'
]

# Email patterns to avoid (likely spam traps or generic)
AVOID_PATTERNS = [
    r'example\.com',
    r'test@',
    r'noreply@',
    r'no-reply@',
    r'donotreply@',
    r'admin@',
    r'postmaster@',
    r'webmaster@',
    r'info@.*\.png',  # Sometimes in images
    r'email@example'
]

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def is_valid_email(email: str) -> bool:
    """
    Validate email address format and check against avoid patterns.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid and not in avoid list
    """
    if not email or len(email) < 5:
        return False
    
    # Check basic format
    if not re.match(EMAIL_PATTERN, email):
        return False
    
    # Check against avoid patterns
    email_lower = email.lower()
    for pattern in AVOID_PATTERNS:
        if re.search(pattern, email_lower):
            return False
    
    # Validate domain
    try:
        domain = email.split('@')[1]
        # Basic domain validation
        if '.' not in domain or len(domain) < 4:
            return False
        return True
    except Exception:
        return False

def calculate_email_confidence(email: str, context: dict) -> float:
    """
    Calculate confidence score for an email address based on context.
    
    Args:
        email: Email address
        context: Dictionary with context info (source_page, in_mailto, etc.)
        
    Returns:
        Confidence score between 0 and 1
    """
    score = 0.5  # Base score
    
    # Higher confidence if found in mailto link
    if context.get('in_mailto'):
        score += 0.3
    
    # Higher confidence if found on contact page
    if context.get('source_page', '').lower() in ['contact', 'contact-us', 'contactus']:
        score += 0.2
    
    # Lower confidence for generic emails
    email_lower = email.lower()
    if any(word in email_lower for word in ['info@', 'support@', 'sales@', 'contact@']):
        score -= 0.1
    
    # Higher confidence for personal emails
    if any(word in email_lower for word in ['@gmail', '@outlook', '@yahoo', '@hotmail']):
        score += 0.1
    
    # Cap between 0 and 1
    return max(0.0, min(1.0, score))

def extract_emails_from_text(text: str) -> Set[str]:
    """
    Extract all email addresses from text.
    
    Args:
        text: Text content to search
        
    Returns:
        Set of unique valid email addresses
    """
    emails = set(re.findall(EMAIL_PATTERN, text, re.IGNORECASE))
    return {email for email in emails if is_valid_email(email)}

@retry_with_backoff
def scrape_page_for_emails(url: str, timeout: int = 10) -> Dict:
    """
    Scrape a single page for email addresses.
    
    Args:
        url: Page URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with emails, metadata, and confidence scores
    """
    if not url or not url.startswith(('http://', 'https://')):
        if url:
            url = f'https://{url}'
        else:
            return {'emails': {}, 'metadata': {}}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        email_data = {}
        
        # Extract from text content
        text_content = soup.get_text()
        text_emails = extract_emails_from_text(text_content)
        
        for email in text_emails:
            email_data[email] = {
                'confidence': calculate_email_confidence(email, {'source_page': url}),
                'source': 'text_content',
                'page': url
            }
        
        # Extract from mailto links (higher confidence)
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0].strip()
                if is_valid_email(email):
                    email_data[email] = {
                        'confidence': calculate_email_confidence(
                            email, 
                            {'in_mailto': True, 'source_page': url}
                        ),
                        'source': 'mailto_link',
                        'page': url
                    }
        
        logger.info(f"Found {len(email_data)} emails on {url}")
        
        return {
            'emails': email_data,
            'metadata': {
                'url': url,
                'status_code': response.status_code,
                'scraped_at': time.time()
            }
        }
        
    except Exception as e:
        logger.warning(f"Failed to scrape {url}: {str(e)}")
        return {'emails': {}, 'metadata': {'url': url, 'error': str(e)}}

def find_contact_pages(base_url: str, max_pages: int = 3) -> List[str]:
    """
    Discover potential contact pages on a website.
    
    Args:
        base_url: Website base URL
        max_pages: Maximum number of pages to return
        
    Returns:
        List of URLs to check for contact information
    """
    if not base_url:
        return []
    
    # Normalize base URL
    if not base_url.startswith(('http://', 'https://')):
        base_url = f'https://{base_url}'
    
    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    
    # Build list of potential contact pages
    pages_to_check = []
    
    for path in CONTACT_PAGES[:max_pages * 2]:
        full_url = urljoin(base_domain, path)
        if full_url not in pages_to_check:
            pages_to_check.append(full_url)
    
    return pages_to_check[:max_pages]

def find_emails(
    website: str,
    max_pages: int = 3,
    use_hunter_api: bool = False
) -> Dict[str, any]:
    """
    Find email addresses from a website by scraping multiple pages.
    
    Args:
        website: Website URL or domain
        max_pages: Maximum pages to scrape
        use_hunter_api: Whether to use Hunter.io API as fallback
        
    Returns:
        Dictionary with found emails, confidence scores, and metadata
    """
    logger.info(f"Starting email search for {website}")
    
    # Load config
    config = load_config()
    research_config = config.get('ai_agent', {}).get('research', {})
    timeout = research_config.get('timeout', 10)
    
    # Find pages to check
    pages_to_check = find_contact_pages(website, max_pages)
    
    all_emails = {}
    pages_scraped = []
    
    # Scrape each page
    for page_url in pages_to_check:
        try:
            result = scrape_page_for_emails(page_url, timeout)
            
            # Merge emails, keeping highest confidence score
            for email, data in result['emails'].items():
                if email not in all_emails or data['confidence'] > all_emails[email]['confidence']:
                    all_emails[email] = data
            
            if result['emails']:
                pages_scraped.append(page_url)
            
            # Small delay between requests
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"Error scraping {page_url}: {str(e)}")
            continue
    
    # Sort emails by confidence
    sorted_emails = dict(
        sorted(all_emails.items(), key=lambda x: x[1]['confidence'], reverse=True)
    )
    
    result = {
        'emails': list(sorted_emails.keys()),
        'email_details': sorted_emails,
        'pages_scraped': pages_scraped,
        'total_found': len(sorted_emails),
        'highest_confidence': max([e['confidence'] for e in sorted_emails.values()]) if sorted_emails else 0
    }
    
    logger.info(f"Found {result['total_found']} emails for {website}")
    
    # Fallback to Hunter.io if no emails found and API is available
    if use_hunter_api and result['total_found'] == 0:
        try:
            hunter_result = find_emails_hunter_api(website)
            if hunter_result:
                result.update(hunter_result)
                logger.info(f"Found emails using Hunter.io API")
        except Exception as e:
            logger.warning(f"Hunter.io API failed: {str(e)}")
    
    return result

def find_emails_hunter_api(domain: str) -> Optional[Dict]:
    """
    Use Hunter.io API to find email addresses (fallback method).
    
    Args:
        domain: Domain name to search
        
    Returns:
        Dictionary with email data or None if not available
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('HUNTER_API_KEY')
    
    if not api_key or api_key == 'your_hunter_api_key_here':
        return None
    
    try:
        # Extract domain from URL if needed
        if domain.startswith(('http://', 'https://')):
            parsed = urlparse(domain)
            domain = parsed.netloc
        
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('data', {}).get('emails'):
            emails = []
            email_details = {}
            
            for email_data in data['data']['emails']:
                email = email_data.get('value')
                if email and is_valid_email(email):
                    emails.append(email)
                    email_details[email] = {
                        'confidence': email_data.get('confidence', 50) / 100,  # Convert to 0-1
                        'source': 'hunter_api',
                        'page': domain,
                        'type': email_data.get('type', 'unknown')
                    }
            
            return {
                'emails': emails,
                'email_details': email_details,
                'total_found': len(emails),
                'source': 'hunter_api'
            }
    
    except Exception as e:
        logger.error(f"Hunter.io API error: {str(e)}")
        return None

def enrich_lead_with_emails(lead: Dict, max_pages: int = 3) -> Dict:
    """
    Enrich a lead dictionary with email addresses.
    
    Args:
        lead: Lead dictionary with at least 'website' field
        max_pages: Maximum pages to scrape per website
        
    Returns:
        Enriched lead dictionary with emails field
    """
    website = lead.get('website')
    
    if not website:
        logger.info(f"No website for lead: {lead.get('business_name', 'Unknown')}")
        lead['emails'] = []
        lead['email_confidence'] = 0
        return lead
    
    # Find emails
    email_result = find_emails(website, max_pages=max_pages)
    
    # Add to lead
    lead['emails'] = email_result['emails']
    lead['email_details'] = email_result['email_details']
    lead['email_confidence'] = email_result['highest_confidence']
    lead['pages_scraped_for_emails'] = email_result['pages_scraped']
    
    return lead

if __name__ == "__main__":
    # Test the email finder
    import sys
    
    if len(sys.argv) > 1:
        test_website = sys.argv[1]
        print(f"\nTesting email finder on: {test_website}")
        
        result = find_emails(test_website, max_pages=3)
        
        print(f"\nFound {result['total_found']} email(s):")
        for email, details in result.get('email_details', {}).items():
            print(f"  - {email}")
            print(f"    Confidence: {details['confidence']:.2f}")
            print(f"    Source: {details['source']}")
            print(f"    Page: {details['page']}")
    else:
        print("Usage: python email_finder.py <website_url>")

