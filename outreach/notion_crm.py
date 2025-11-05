"""Notion CRM integration for lead tracking and management."""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
from notion_client import Client
from notion_client.errors import APIResponseError
from utils.logger import setup_logger
import yaml

logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

class NotionCRM:
    """Notion CRM integration for managing leads and outreach."""
    
    def __init__(self):
        """Initialize Notion client."""
        self.api_key = os.getenv('NOTION_API_KEY')
        self.database_id = os.getenv('NOTION_DATABASE_ID')
        
        if not self.api_key or self.api_key == 'your_notion_integration_key_here':
            logger.warning("Notion API key not configured")
            self.client = None
        else:
            try:
                self.client = Client(auth=self.api_key)
                logger.info("Notion client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Notion client: {e}")
                self.client = None
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from config.yaml."""
        try:
            with open("config.yaml", "r") as f:
                config = yaml.safe_load(f)
                return config.get('ai_agent', {}).get('notion', {})
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def is_configured(self) -> bool:
        """Check if Notion is properly configured."""
        return self.client is not None and self.database_id and self.database_id != 'your_notion_database_id_here'
    
    def create_database(self, parent_page_id: str, title: str = "Lead Outreach CRM") -> Optional[str]:
        """
        Create a new Notion database with the proper schema for lead tracking.
        
        Args:
            parent_page_id: Notion page ID where database will be created
            title: Database title
            
        Returns:
            Database ID if successful, None otherwise
        """
        if not self.client:
            logger.error("Notion client not initialized")
            return None
        
        try:
            # Define database schema
            database_schema = {
                "parent": {"page_id": parent_page_id},
                "title": [{"type": "text", "text": {"content": title}}],
                "properties": {
                    "Business Name": {"title": {}},
                    "Phone": {"rich_text": {}},
                    "Website": {"url": {}},
                    "Address": {"rich_text": {}},
                    "Rating": {"rich_text": {}},
                    
                    # Contact Information
                    "Emails": {"rich_text": {}},
                    "Email Confidence": {"number": {"format": "percent"}},
                    
                    # AI Research
                    "Quality Score": {"number": {"format": "number"}},
                    "AI Insights": {"rich_text": {}},
                    "Pain Points": {"rich_text": {}},
                    "Tech Stack": {"multi_select": {"options": []}},
                    
                    # Outreach Status
                    "Status": {
                        "select": {
                            "options": [
                                {"name": "New", "color": "gray"},
                                {"name": "Researching", "color": "blue"},
                                {"name": "Qualified", "color": "green"},
                                {"name": "Ready to Contact", "color": "yellow"},
                                {"name": "Email Sent", "color": "orange"},
                                {"name": "Replied", "color": "purple"},
                                {"name": "Not Qualified", "color": "red"},
                                {"name": "Bounced", "color": "red"}
                            ]
                        }
                    },
                    
                    # Email Details
                    "Email Subject": {"rich_text": {}},
                    "Email Body": {"rich_text": {}},
                    "Email Sent Date": {"date": {}},
                    
                    # Analytics
                    "Opened": {"checkbox": {}},
                    "Replied": {"checkbox": {}},
                    "Follow Up Date": {"date": {}},
                    
                    # Tags and Campaign
                    "Tags": {"multi_select": {"options": []}},
                    "Campaign": {"select": {"options": []}},
                    "Priority": {
                        "select": {
                            "options": [
                                {"name": "High", "color": "red"},
                                {"name": "Medium", "color": "yellow"},
                                {"name": "Low", "color": "gray"}
                            ]
                        }
                    },
                    
                    # Metadata
                    "Source": {"select": {"options": [
                        {"name": "Google Maps", "color": "blue"},
                        {"name": "Manual", "color": "gray"}
                    ]}},
                    "Created Date": {"created_time": {}},
                    "Last Updated": {"last_edited_time": {}}
                }
            }
            
            response = self.client.databases.create(**database_schema)
            database_id = response['id']
            
            logger.info(f"Created Notion database: {database_id}")
            return database_id
            
        except Exception as e:
            logger.error(f"Failed to create Notion database: {e}")
            return None
    
    def create_lead_entry(self, lead: Dict) -> Optional[str]:
        """
        Create a new lead entry in Notion database.
        
        Args:
            lead: Lead dictionary with all information
            
        Returns:
            Page ID if successful, None otherwise
        """
        if not self.is_configured():
            logger.warning("Notion not configured, skipping lead creation")
            return None
        
        try:
            # Prepare properties
            properties = {
                "Business Name": {
                    "title": [{"text": {"content": lead.get('business_name', 'Unknown')[:2000]}}]
                },
                "Phone": {
                    "rich_text": [{"text": {"content": lead.get('phone', '')[:2000]}}]
                },
                "Website": {
                    "url": lead.get('website', '')[:2000] if lead.get('website') else None
                },
                "Address": {
                    "rich_text": [{"text": {"content": lead.get('address', '')[:2000]}}]
                },
                "Rating": {
                    "rich_text": [{"text": {"content": str(lead.get('rating', ''))[:2000]}}]
                },
                "Status": {
                    "select": {"name": lead.get('status', 'New')}
                },
                "Source": {
                    "select": {"name": lead.get('source', 'Google Maps')}
                },
            }
            
            # Add emails if present
            if lead.get('emails'):
                emails_str = ', '.join(lead['emails'][:5])  # Limit to 5 emails
                properties["Emails"] = {
                    "rich_text": [{"text": {"content": emails_str[:2000]}}]
                }
            
            # Add email confidence
            if 'email_confidence' in lead:
                properties["Email Confidence"] = {
                    "number": lead['email_confidence']
                }
            
            # Add AI insights
            if lead.get('ai_insights'):
                properties["AI Insights"] = {
                    "rich_text": [{"text": {"content": str(lead['ai_insights'])[:2000]}}]
                }
            
            # Add quality score
            if 'quality_score' in lead:
                properties["Quality Score"] = {
                    "number": lead['quality_score']
                }
            
            # Add pain points
            if lead.get('pain_points'):
                pain_points_str = ', '.join(lead['pain_points']) if isinstance(lead['pain_points'], list) else str(lead['pain_points'])
                properties["Pain Points"] = {
                    "rich_text": [{"text": {"content": pain_points_str[:2000]}}]
                }
            
            # Add tech stack
            if lead.get('technologies'):
                tech_options = [{"name": tech} for tech in lead['technologies'][:5]]
                properties["Tech Stack"] = {
                    "multi_select": tech_options
                }
            
            # Add email details if sent
            if lead.get('email_subject'):
                properties["Email Subject"] = {
                    "rich_text": [{"text": {"content": lead['email_subject'][:2000]}}]
                }
            
            if lead.get('email_body'):
                properties["Email Body"] = {
                    "rich_text": [{"text": {"content": lead['email_body'][:2000]}}]
                }
            
            if lead.get('email_sent_date'):
                properties["Email Sent Date"] = {
                    "date": {"start": lead['email_sent_date']}
                }
            
            # Add tags
            if lead.get('tags'):
                tag_options = [{"name": tag} for tag in lead['tags'][:5]]
                properties["Tags"] = {
                    "multi_select": tag_options
                }
            
            # Create page
            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties
            )
            
            page_id = response['id']
            logger.info(f"Created Notion entry for {lead.get('business_name', 'Unknown')}: {page_id}")
            return page_id
            
        except APIResponseError as e:
            logger.error(f"Notion API error creating lead: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create lead entry: {e}")
            return None
    
    def update_lead_status(self, page_id: str, status: str, additional_data: Optional[Dict] = None) -> bool:
        """
        Update lead status and optionally other fields.
        
        Args:
            page_id: Notion page ID
            status: New status value
            additional_data: Optional dictionary with other fields to update
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            return False
        
        try:
            properties = {
                "Status": {"select": {"name": status}}
            }
            
            # Add additional data if provided
            if additional_data:
                if 'email_sent_date' in additional_data:
                    properties["Email Sent Date"] = {
                        "date": {"start": additional_data['email_sent_date']}
                    }
                
                if 'replied' in additional_data:
                    properties["Replied"] = {"checkbox": additional_data['replied']}
                
                if 'quality_score' in additional_data:
                    properties["Quality Score"] = {"number": additional_data['quality_score']}
            
            self.client.pages.update(page_id=page_id, properties=properties)
            logger.info(f"Updated lead status to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update lead status: {e}")
            return False
    
    def sync_from_json(self, json_file_path: str, campaign: Optional[str] = None) -> Dict[str, int]:
        """
        Import leads from JSON file to Notion database.
        
        Args:
            json_file_path: Path to JSON file with leads
            campaign: Optional campaign name to tag leads with
            
        Returns:
            Dictionary with sync statistics
        """
        if not self.is_configured():
            logger.warning("Notion not configured, skipping sync")
            return {'success': 0, 'failed': 0, 'skipped': 0}
        
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        try:
            # Load JSON file
            with open(json_file_path, 'r', encoding='utf-8') as f:
                leads = json.load(f)
            
            logger.info(f"Syncing {len(leads)} leads from {json_file_path}")
            
            # Process each lead
            for lead in leads:
                try:
                    # Add campaign tag if provided
                    if campaign:
                        lead['tags'] = lead.get('tags', []) + [campaign]
                    
                    # Set default status if not present
                    if 'status' not in lead:
                        lead['status'] = 'New'
                    
                    # Create entry
                    page_id = self.create_lead_entry(lead)
                    
                    if page_id:
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                    
                except Exception as e:
                    logger.error(f"Error syncing lead {lead.get('business_name', 'Unknown')}: {e}")
                    stats['failed'] += 1
            
            logger.info(f"Sync complete: {stats['success']} success, {stats['failed']} failed")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to sync from JSON: {e}")
            return stats
    
    def get_leads_by_status(self, status: str, limit: int = 100) -> List[Dict]:
        """
        Query leads by status.
        
        Args:
            status: Status to filter by
            limit: Maximum number of results
            
        Returns:
            List of lead dictionaries
        """
        if not self.is_configured():
            return []
        
        try:
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Status",
                    "select": {"equals": status}
                },
                page_size=min(limit, 100)
            )
            
            leads = []
            for page in response['results']:
                lead = self._parse_notion_page(page)
                leads.append(lead)
            
            logger.info(f"Retrieved {len(leads)} leads with status: {status}")
            return leads
            
        except Exception as e:
            logger.error(f"Failed to query leads: {e}")
            return []
    
    def _parse_notion_page(self, page: Dict) -> Dict:
        """Parse Notion page into lead dictionary."""
        props = page['properties']
        
        lead = {
            'notion_page_id': page['id'],
            'notion_url': page['url'],
        }
        
        # Extract title
        if 'Business Name' in props and props['Business Name']['title']:
            lead['business_name'] = props['Business Name']['title'][0]['text']['content']
        
        # Extract other properties
        for prop_name, prop_data in props.items():
            prop_type = prop_data['type']
            
            if prop_type == 'rich_text' and prop_data['rich_text']:
                lead[prop_name.lower().replace(' ', '_')] = prop_data['rich_text'][0]['text']['content']
            elif prop_type == 'url' and prop_data['url']:
                lead[prop_name.lower().replace(' ', '_')] = prop_data['url']
            elif prop_type == 'select' and prop_data['select']:
                lead[prop_name.lower().replace(' ', '_')] = prop_data['select']['name']
            elif prop_type == 'number' and prop_data['number'] is not None:
                lead[prop_name.lower().replace(' ', '_')] = prop_data['number']
            elif prop_type == 'checkbox':
                lead[prop_name.lower().replace(' ', '_')] = prop_data['checkbox']
        
        return lead
    
    def log_email_activity(self, page_id: str, activity: Dict) -> bool:
        """
        Log email activity for a lead.
        
        Args:
            page_id: Notion page ID
            activity: Dictionary with activity details
            
        Returns:
            True if successful
        """
        if not self.is_configured():
            return False
        
        try:
            properties = {}
            
            if activity.get('sent'):
                properties["Email Sent Date"] = {
                    "date": {"start": activity.get('sent_date', datetime.now().isoformat())}
                }
                properties["Status"] = {"select": {"name": "Email Sent"}}
            
            if activity.get('opened'):
                properties["Opened"] = {"checkbox": True}
            
            if activity.get('replied'):
                properties["Replied"] = {"checkbox": True}
                properties["Status"] = {"select": {"name": "Replied"}}
            
            if activity.get('bounced'):
                properties["Status"] = {"select": {"name": "Bounced"}}
            
            if properties:
                self.client.pages.update(page_id=page_id, properties=properties)
                logger.info(f"Logged email activity for page {page_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to log email activity: {e}")
            return False

# Global instance
notion_crm = NotionCRM()

if __name__ == "__main__":
    # Test Notion integration
    print("Testing Notion CRM integration...")
    
    if notion_crm.is_configured():
        print("✓ Notion is configured")
        
        # Test creating a sample lead
        test_lead = {
            'business_name': 'Test Business',
            'phone': '123-456-7890',
            'website': 'https://example.com',
            'address': '123 Test St',
            'rating': '4.5',
            'emails': ['test@example.com'],
            'email_confidence': 0.8,
            'quality_score': 75,
            'status': 'New',
            'source': 'Google Maps'
        }
        
        page_id = notion_crm.create_lead_entry(test_lead)
        if page_id:
            print(f"✓ Created test lead: {page_id}")
        else:
            print("✗ Failed to create test lead")
    else:
        print("✗ Notion not configured. Please set NOTION_API_KEY and NOTION_DATABASE_ID in .env file")

