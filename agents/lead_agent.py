"""Main AI agent for lead outreach using LangChain."""
from typing import Dict, List, Optional, Callable
import json
from langchain.tools import Tool
try:
    from langchain.agents import AgentExecutor, create_react_agent
except ImportError:
    # Fallback for newer langchain versions
    from langchain_core.agents import AgentExecutor
    from langchain.agents import create_react_agent
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
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

class LeadOutreachAgent:
    """AI agent for autonomous lead research and outreach."""
    
    def __init__(
        self,
        on_lead_processed: Optional[Callable] = None,
        on_status_update: Optional[Callable] = None
    ):
        """
        Initialize the AI agent.
        
        Args:
            on_lead_processed: Callback when a lead is processed
            on_status_update: Callback for status updates
        """
        self.config = load_config()
        self.on_lead_processed = on_lead_processed
        self.on_status_update = on_status_update
        
        # Initialize Gemini
        if not initialize_gemini():
            raise ValueError("Failed to initialize Gemini API")
        
        # Initialize LangChain LLM
        model_config = self.config.get('ai_agent', {}).get('model', {})
        self.llm = ChatGoogleGenerativeAI(
            model=model_config.get('name', 'gemini-1.5-flash'),
            temperature=model_config.get('temperature', 0.7),
            google_api_key=os.getenv('GEMINI_API_KEY')
        )
        
        logger.info("LeadOutreachAgent initialized")
    
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
        """
        Process a single lead through the complete pipeline.
        
        Args:
            lead: Lead dictionary
            find_email: Whether to find email addresses
            do_research: Whether to do AI research
            generate_email: Whether to generate outreach email
            
        Returns:
            Processed lead dictionary
        """
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
        """
        Process multiple leads in batch.
        
        Args:
            leads: List of lead dictionaries
            find_email: Whether to find email addresses
            do_research: Whether to do AI research
            generate_email: Whether to generate outreach emails
            sync_to_notion: Whether to sync to Notion CRM
            
        Returns:
            Dictionary with processing statistics
        """
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
    
    def decide_next_action(self, lead: Dict) -> str:
        """
        Use AI to decide the next best action for a lead.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            Recommended action
        """
        context = f"""Lead Analysis:
Business: {lead.get('business_name')}
Quality Score: {lead.get('quality_score', 'N/A')}
Has Email: {bool(lead.get('emails'))}
Research Complete: {lead.get('research_status') == 'completed'}
Email Generated: {lead.get('email_status') == 'generated'}
Status: {lead.get('status', 'Unknown')}"""
        
        if lead.get('ai_insights'):
            context += f"\n\nAI Insights:"
            context += f"\nSummary: {lead['ai_insights'].get('business_summary', 'N/A')}"
            context += f"\nPain Points: {', '.join(lead['ai_insights'].get('pain_points', []))}"
        
        prompt = f"""{context}

Based on this lead's information, what should be the next action?

Options:
1. SEND_EMAIL - Ready to send outreach email
2. NEEDS_RESEARCH - Needs more research before outreach
3. FIND_EMAIL - Need to find contact email
4. DISQUALIFY - Lead doesn't meet qualification criteria
5. FOLLOW_UP - Need to follow up on previous outreach
6. SKIP - Not a good fit for outreach

Respond with ONLY the action code (e.g., SEND_EMAIL) and a brief one-line reason."""
        
        try:
            response = self.llm.invoke(prompt)
            decision = response.content.strip()
            
            logger.info(f"AI decision for {lead.get('business_name')}: {decision}")
            return decision
            
        except Exception as e:
            logger.error(f"Error in AI decision making: {e}")
            return "ERROR - Could not determine next action"
    
    def qualify_lead(self, lead: Dict) -> bool:
        """
        Determine if a lead is qualified for outreach.
        
        Args:
            lead: Lead dictionary
            
        Returns:
            True if qualified, False otherwise
        """
        min_score = self.config.get('ai_agent', {}).get('qualification', {}).get('min_score', 60)
        quality_score = lead.get('quality_score', 0)
        
        return quality_score >= min_score
    
    def get_agent_stats(self) -> Dict:
        """
        Get agent statistics and status.
        
        Returns:
            Dictionary with agent stats
        """
        return {
            'configured': initialize_gemini(),
            'notion_configured': notion_crm.is_configured(),
            'model': self.config.get('ai_agent', {}).get('model', {}).get('name', 'gemini-pro'),
            'min_quality_score': self.config.get('ai_agent', {}).get('qualification', {}).get('min_score', 60)
        }

def create_agent_with_tools() -> AgentExecutor:
    """
    Create a LangChain agent with custom tools.
    
    Returns:
        Configured AgentExecutor
    """
    # Initialize Gemini
    if not initialize_gemini():
        raise ValueError("Failed to initialize Gemini API")
    
    config = load_config()
    model_config = config.get('ai_agent', {}).get('model', {})
    
    llm = ChatGoogleGenerativeAI(
        model=model_config.get('name', 'gemini-1.5-flash'),
        temperature=model_config.get('temperature', 0.7),
        google_api_key=os.getenv('GEMINI_API_KEY')
    )
    
    # Define tools
    tools = [
        Tool(
            name="find_email",
            func=lambda website: json.dumps(find_emails(website)),
            description="Find email addresses from a business website. Input should be a website URL."
        ),
        Tool(
            name="research_business",
            func=lambda lead_json: json.dumps(research_lead(json.loads(lead_json))),
            description="Research a business using AI. Input should be a JSON string with lead information including business_name and website."
        ),
        Tool(
            name="generate_email",
            func=lambda lead_json: json.dumps(generate_complete_email(json.loads(lead_json))),
            description="Generate a personalized outreach email. Input should be a JSON string with lead information."
        )
    ]
    
    # Create agent prompt
    template = """You are an AI agent specialized in lead generation and outreach.

You have access to the following tools:
{tools}

Tool Names: {tool_names}

Use the following format:
Thought: Think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Question: {input}
{agent_scratchpad}"""
    
    prompt = PromptTemplate.from_template(template)
    
    # Create agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

if __name__ == "__main__":
    # Test agent
    print("Testing Lead Outreach Agent...")
    
    try:
        agent = LeadOutreachAgent()
        print("✓ Agent initialized successfully")
        
        stats = agent.get_agent_stats()
        print(f"\nAgent Stats:")
        print(f"  Configured: {stats['configured']}")
        print(f"  Notion Configured: {stats['notion_configured']}")
        print(f"  Model: {stats['model']}")
        print(f"  Min Quality Score: {stats['min_quality_score']}")
        
        # Test with sample lead
        test_lead = {
            'business_name': 'Test Business',
            'website': 'https://example.com',
            'phone': '123-456-7890'
        }
        
        print(f"\nTesting lead processing (dry run)...")
        # Don't actually process, just test initialization
        print("✓ Agent ready to process leads")
        
    except Exception as e:
        print(f"✗ Failed to initialize agent: {e}")

