"""AI-powered lead research module using Gemini."""
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from utils.logger import setup_logger
from utils.ai_helpers import generate_text, extract_json_from_response
from utils.decorators import retry_with_backoff
import yaml
import json

logger = setup_logger(__name__)

def load_config() -> dict:
    """Load configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

@retry_with_backoff
def scrape_website_content(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Scrape website content for AI analysis.
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dictionary with scraped content and metadata
    """
    if not url or not url.startswith(('http://', 'https://')):
        if url:
            url = f'https://{url}'
        else:
            return {'success': False, 'error': 'Invalid URL'}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'footer']):
            element.decompose()
        
        # Extract text content
        text_content = soup.get_text(separator=' ', strip=True)
        
        # Limit content length for AI processing
        max_chars = 5000
        if len(text_content) > max_chars:
            text_content = text_content[:max_chars] + "..."
        
        # Extract headings
        headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        # Extract meta description
        meta_desc = None
        meta_tag = soup.find('meta', attrs={'name': 'description'})
        if meta_tag and meta_tag.get('content'):
            meta_desc = meta_tag['content']
        
        return {
            'success': True,
            'url': url,
            'text_content': text_content,
            'headings': headings[:10],  # Limit to 10 headings
            'meta_description': meta_desc,
            'title': soup.title.string if soup.title else None
        }
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {str(e)}")
        return {
            'success': False,
            'url': url,
            'error': str(e)
        }

def scrape_multiple_pages(base_url: str, max_pages: int = 3) -> List[Dict]:
    """
    Scrape multiple pages from a website.
    
    Args:
        base_url: Base website URL
        max_pages: Maximum pages to scrape
        
    Returns:
        List of scraped page data
    """
    config = load_config()
    research_config = config.get('ai_agent', {}).get('research', {})
    pages_to_check = research_config.get('pages_to_check', ['/', '/about', '/contact'])
    
    if not base_url.startswith(('http://', 'https://')):
        base_url = f'https://{base_url}'
    
    parsed = urlparse(base_url)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    
    scraped_pages = []
    
    for i, path in enumerate(pages_to_check[:max_pages]):
        if i >= max_pages:
            break
        
        full_url = urljoin(base_domain, path)
        result = scrape_website_content(full_url)
        
        if result.get('success'):
            scraped_pages.append(result)
        
        # Small delay between requests
        time.sleep(1)
    
    return scraped_pages

def analyze_website_with_ai(website_data: List[Dict], business_name: str) -> Optional[Dict]:
    """
    Use AI to analyze website content and extract insights.
    
    Args:
        website_data: List of scraped page data
        business_name: Name of the business
        
    Returns:
        Dictionary with AI-generated insights
    """
    if not website_data or not any(page.get('success') for page in website_data):
        logger.warning(f"No valid website data for {business_name}")
        return None
    
    # Combine content from all pages
    combined_content = ""
    for page in website_data:
        if page.get('success'):
            combined_content += f"\n\n--- Page: {page['url']} ---\n"
            if page.get('title'):
                combined_content += f"Title: {page['title']}\n"
            if page.get('meta_description'):
                combined_content += f"Description: {page['meta_description']}\n"
            if page.get('headings'):
                combined_content += f"Headings: {', '.join(page['headings'][:5])}\n"
            combined_content += f"Content: {page['text_content'][:1500]}\n"
    
    # Create AI prompt
    prompt = f"""Analyze this business website and provide detailed insights in JSON format.

Business Name: {business_name}

Website Content:
{combined_content}

Please analyze and return a JSON object with the following structure:
{{
    "business_summary": "Brief 2-3 sentence summary of what this business does",
    "industry": "Primary industry/sector",
    "services_products": ["List of main services or products offered"],
    "target_audience": "Who their target customers are",
    "pain_points": ["Potential pain points or challenges this business might face"],
    "unique_value_proposition": "What makes them unique or special",
    "business_size": "Estimated business size (small/medium/large/enterprise)",
    "quality_indicators": ["Positive indicators about business quality"],
    "red_flags": ["Any concerns or red flags"],
    "outreach_angles": ["Suggested angles for outreach based on their needs"]
}}

Return ONLY the JSON object, no other text."""
    
    try:
        response = generate_text(prompt)
        
        if not response:
            logger.error("No response from AI for website analysis")
            return None
        
        # Extract JSON from response
        analysis = extract_json_from_response(response)
        
        if analysis:
            logger.info(f"Successfully analyzed website for {business_name}")
            return analysis
        else:
            # If JSON extraction fails, return basic structure with raw response
            logger.warning(f"Could not parse AI response as JSON for {business_name}")
            return {
                'business_summary': response[:500],
                'raw_analysis': response
            }
            
    except Exception as e:
        logger.error(f"Error analyzing website with AI: {str(e)}")
        return None

def calculate_quality_score(lead: Dict, ai_insights: Optional[Dict]) -> int:
    """
    Calculate quality score for a lead based on available data and AI insights.
    
    Args:
        lead: Lead dictionary
        ai_insights: AI-generated insights
        
    Returns:
        Quality score (0-100)
    """
    config = load_config()
    weights = config.get('ai_agent', {}).get('qualification', {}).get('score_weights', {})
    
    score = 0
    max_score = 100
    
    # Website quality (30 points)
    website_score = 0
    if lead.get('website'):
        website_score += 10  # Has website
        if ai_insights:
            website_score += 10  # Successfully analyzed
            if ai_insights.get('unique_value_proposition'):
                website_score += 5
            if ai_insights.get('quality_indicators'):
                website_score += 5
    score += website_score * weights.get('website_quality', 0.3) / 0.3
    
    # Business info completeness (20 points)
    info_score = 0
    if lead.get('phone'):
        info_score += 7
    if lead.get('address'):
        info_score += 7
    if lead.get('rating'):
        info_score += 6
    score += info_score * weights.get('business_info_completeness', 0.2) / 0.2
    
    # Contact availability (20 points)
    contact_score = 0
    if lead.get('emails') and len(lead['emails']) > 0:
        contact_score += 10
        if lead.get('email_confidence', 0) > 0.7:
            contact_score += 5
    if lead.get('phone'):
        contact_score += 5
    score += contact_score * weights.get('contact_availability', 0.2) / 0.2
    
    # Relevance (30 points)
    relevance_score = 15  # Base score
    if ai_insights:
        if ai_insights.get('pain_points') and len(ai_insights.get('pain_points', [])) > 0:
            relevance_score += 8
        if ai_insights.get('outreach_angles') and len(ai_insights.get('outreach_angles', [])) > 0:
            relevance_score += 7
        if ai_insights.get('red_flags') and len(ai_insights.get('red_flags', [])) > 0:
            relevance_score -= 5  # Deduct for red flags
    score += relevance_score * weights.get('relevance', 0.3) / 0.3
    
    # Ensure score is between 0 and 100
    final_score = max(0, min(100, int(score)))
    
    return final_score

def research_lead(lead: Dict, max_pages: int = 3) -> Dict:
    """
    Conduct comprehensive AI-powered research on a lead.
    
    Args:
        lead: Lead dictionary with at least business_name and website
        max_pages: Maximum pages to scrape per website
        
    Returns:
        Enhanced lead dictionary with research findings
    """
    business_name = lead.get('business_name', 'Unknown')
    website = lead.get('website')
    
    logger.info(f"Researching lead: {business_name}")
    
    # Initialize research results
    lead['research_status'] = 'in_progress'
    lead['ai_insights'] = None
    lead['quality_score'] = 0
    
    if not website:
        logger.info(f"No website for {business_name}, skipping AI research")
        lead['research_status'] = 'no_website'
        lead['quality_score'] = calculate_quality_score(lead, None)
        return lead
    
    try:
        # Scrape website content
        website_data = scrape_multiple_pages(website, max_pages)
        
        if not website_data:
            logger.warning(f"No data scraped for {business_name}")
            lead['research_status'] = 'scraping_failed'
            lead['quality_score'] = calculate_quality_score(lead, None)
            return lead
        
        # Analyze with AI
        ai_insights = analyze_website_with_ai(website_data, business_name)
        
        if ai_insights:
            lead['ai_insights'] = ai_insights
            lead['research_status'] = 'completed'
            
            # Extract specific fields for easier access
            lead['business_summary'] = ai_insights.get('business_summary', '')
            lead['industry'] = ai_insights.get('industry', '')
            lead['pain_points'] = ai_insights.get('pain_points', [])
            lead['outreach_angles'] = ai_insights.get('outreach_angles', [])
            lead['target_audience'] = ai_insights.get('target_audience', '')
        else:
            logger.warning(f"AI analysis failed for {business_name}")
            lead['research_status'] = 'ai_analysis_failed'
        
        # Calculate quality score
        lead['quality_score'] = calculate_quality_score(lead, ai_insights)
        
        logger.info(f"Research completed for {business_name} - Quality Score: {lead['quality_score']}")
        
        return lead
        
    except Exception as e:
        logger.error(f"Error researching lead {business_name}: {str(e)}")
        lead['research_status'] = 'error'
        lead['research_error'] = str(e)
        lead['quality_score'] = calculate_quality_score(lead, None)
        return lead

def batch_research_leads(leads: List[Dict], max_pages: int = 3, delay: float = 2.0) -> List[Dict]:
    """
    Research multiple leads in batch with rate limiting.
    
    Args:
        leads: List of lead dictionaries
        max_pages: Maximum pages to scrape per website
        delay: Delay between requests in seconds
        
    Returns:
        List of researched leads
    """
    logger.info(f"Starting batch research for {len(leads)} leads")
    
    researched_leads = []
    
    for i, lead in enumerate(leads):
        logger.info(f"Researching lead {i+1}/{len(leads)}")
        
        researched_lead = research_lead(lead, max_pages)
        researched_leads.append(researched_lead)
        
        # Rate limiting delay
        if i < len(leads) - 1:
            time.sleep(delay)
    
    logger.info(f"Batch research completed for {len(researched_leads)} leads")
    
    return researched_leads

def filter_qualified_leads(leads: List[Dict], min_score: int = 60) -> List[Dict]:
    """
    Filter leads based on quality score threshold.
    
    Args:
        leads: List of researched leads
        min_score: Minimum quality score to be considered qualified
        
    Returns:
        List of qualified leads
    """
    qualified = [lead for lead in leads if lead.get('quality_score', 0) >= min_score]
    
    logger.info(f"Filtered {len(qualified)} qualified leads from {len(leads)} total (min score: {min_score})")
    
    return qualified

if __name__ == "__main__":
    # Test lead researcher
    import sys
    
    if len(sys.argv) > 1:
        test_website = sys.argv[1]
        test_name = sys.argv[2] if len(sys.argv) > 2 else "Test Business"
        
        print(f"\nTesting lead researcher on: {test_name} ({test_website})")
        
        test_lead = {
            'business_name': test_name,
            'website': test_website,
            'phone': '123-456-7890'
        }
        
        result = research_lead(test_lead, max_pages=2)
        
        print(f"\nResearch Results:")
        print(f"Status: {result.get('research_status')}")
        print(f"Quality Score: {result.get('quality_score')}")
        
        if result.get('ai_insights'):
            print(f"\nAI Insights:")
            print(json.dumps(result['ai_insights'], indent=2))
    else:
        print("Usage: python lead_researcher.py <website_url> [business_name]")

