"""Website scraper module for enriching lead data."""
import re
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.logger import setup_logger
from utils.decorators import retry_with_backoff

logger = setup_logger(__name__)

# Constants
EMAIL_PATTERN = r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b'
SOCIAL_PATTERNS = {
    'instagram': r'instagram\.com/[\w\.-]+',
    'facebook': r'facebook\.com/[\w\.-]+',
    'linkedin': r'linkedin\.com/(?:company|in)/[\w\.-]+'
}
TECH_PATTERNS = {
    'wordpress': 'wp-content',
    'shopify': 'cdn.shopify.com',
    'magento': 'static/version'
}

def extract_emails(text: str) -> Set[str]:
    """
    Extract email addresses from text using regex.
    
    Args:
        text: Text to search for email addresses
        
    Returns:
        Set of unique email addresses found
    """
    return set(re.findall(EMAIL_PATTERN, text, re.IGNORECASE))

def extract_social_links(soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
    """
    Extract social media profile links from HTML.
    
    Args:
        soup: BeautifulSoup object of parsed HTML
        base_url: Website's base URL for resolving relative links
        
    Returns:
        Dictionary mapping platform names to profile URLs
    """
    social_links = {}
    
    for platform, pattern in SOCIAL_PATTERNS.items():
        for link in soup.find_all('a', href=True):
            href = urljoin(base_url, link['href'])
            if re.search(pattern, href, re.IGNORECASE):
                social_links[platform] = href
                break
    
    return social_links

def detect_technologies(html: str) -> List[str]:
    """
    Detect technologies used on the website.
    
    Args:
        html: Raw HTML content
        
    Returns:
        List of detected technology names
    """
    technologies = []
    
    for tech, pattern in TECH_PATTERNS.items():
        if pattern in html:
            technologies.append(tech)
    
    return technologies

@retry_with_backoff
def scrape_website(url: str, timeout: int = 5) -> Dict:
    """
    Scrape a single website for contact information and social links.
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary containing extracted emails, social links, and tech tags
    """
    if not url:
        return {'emails': set(), 'social_links': {}, 'technologies': []}
    
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract all text content
        text_content = soup.get_text()
        
        # Find emails
        emails = extract_emails(text_content)
        
        # Also check mailto: links
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href.replace('mailto:', '').split('?')[0]
                if re.match(EMAIL_PATTERN, email):
                    emails.add(email)
        
        # Get social links
        social_links = extract_social_links(soup, url)
        
        # Detect technologies
        technologies = detect_technologies(html)
        
        logger.info(f"Successfully scraped {url}")
        logger.info(f"Found {len(emails)} emails and {len(social_links)} social links")
        
        return {
            'emails': emails,
            'social_links': social_links,
            'technologies': technologies
        }
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {'emails': set(), 'social_links': {}, 'technologies': []}

def enrich(leads: List[Dict], on_lead_callback=None) -> List[Dict]:
    """
    Enrich lead data with website information.
    
    Args:
        leads: List of lead dictionaries from Google Maps scraper
        on_lead_callback: Optional callback function to report progress
        
    Returns:
        Enriched list of lead dictionaries with additional fields
    """
    for lead in leads:
        if lead.get('website'):
            logger.info(f"Enriching data for {lead['business_name']}")
            
            # Scrape website
            website_data = scrape_website(lead['website'])
            
            # Update lead with new information
            lead['emails'] = list(website_data['emails'])
            lead['social_links'] = website_data['social_links']
            lead['technologies'] = website_data['technologies']
            
            # Add notes about findings
            notes = []
            if website_data['technologies']:
                notes.append(f"Technologies: {', '.join(website_data['technologies'])}")
            if website_data['social_links']:
                notes.append(f"Social profiles: {', '.join(website_data['social_links'].keys())}")
            
            if lead.get('notes'):
                if notes:
                    lead['notes'] += ' | ' + ' | '.join(notes)
            else:
                lead['notes'] = ' | '.join(notes)
            
            # Call the callback with updated lead info if available
            if on_lead_callback:
                on_lead_callback(lead)
        
        else:
            logger.info(f"No website found for {lead['business_name']}")
            lead.update({
                'emails': [],
                'social_links': {},
                'technologies': [],
                'notes': lead.get('notes', '') + ' | No website available' if lead.get('notes') else 'No website available'
            })
            
            # Call the callback even for leads without websites
            if on_lead_callback:
                on_lead_callback(lead)
    
    return leads

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        print(f"\nTesting website scraper on: {test_url}")
        result = scrape_website(test_url)
        print("\nEmails found:", result['emails'])
        print("Social links:", result['social_links'])
        print("Technologies:", result['technologies'])
    else:
        print("Please provide a URL to test")