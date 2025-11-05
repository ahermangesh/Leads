"""Test script for AI Agent end-to-end workflow."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_configuration():
    """Test that all required configurations are set."""
    print("=" * 50)
    print("Testing Configuration...")
    print("=" * 50)
    
    checks = {
        'Gemini API': os.getenv('GEMINI_API_KEY', 'Not set'),
        'Resend API': os.getenv('RESEND_API_KEY', 'Not set'),
        'Notion API': os.getenv('NOTION_API_KEY', 'Not set'),
        'Sender Email': os.getenv('SENDER_EMAIL', 'Not set'),
    }
    
    all_configured = True
    for name, value in checks.items():
        is_set = value != 'Not set' and 'your_' not in value.lower()
        status = "✓" if is_set else "✗"
        print(f"{status} {name}: {'Configured' if is_set else 'Not configured'}")
        if not is_set:
            all_configured = False
    
    print()
    return all_configured

def test_imports():
    """Test that all required modules can be imported."""
    print("=" * 50)
    print("Testing Imports...")
    print("=" * 50)
    
    modules = [
        ('utils.ai_helpers', 'AI Helpers'),
        ('outreach.email_finder', 'Email Finder'),
        ('outreach.lead_researcher', 'Lead Researcher'),
        ('outreach.email_generator', 'Email Generator'),
        ('outreach.email_sender', 'Email Sender'),
        ('outreach.notion_crm', 'Notion CRM'),
        ('agents.lead_agent', 'Lead Agent'),
        ('agents.orchestrator', 'Orchestrator'),
        ('agents.memory', 'Agent Memory'),
    ]
    
    all_imported = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name}: OK")
        except Exception as e:
            print(f"✗ {display_name}: FAILED - {str(e)}")
            all_imported = False
    
    print()
    return all_imported

def test_ai_connection():
    """Test connection to Gemini AI."""
    print("=" * 50)
    print("Testing AI Connection...")
    print("=" * 50)
    
    try:
        from utils.ai_helpers import initialize_gemini, generate_text
        
        if not initialize_gemini():
            print("✗ Gemini API: Not configured")
            return False
        
        # Test simple generation
        response = generate_text("Say 'Hello' in one word.")
        
        if response:
            print(f"✓ Gemini AI: Connected")
            print(f"  Test response: {response[:50]}...")
            return True
        else:
            print("✗ Gemini AI: No response")
            return False
            
    except Exception as e:
        print(f"✗ Gemini AI: FAILED - {str(e)}")
        return False
    
    finally:
        print()

def test_email_sender():
    """Test email sender configuration."""
    print("=" * 50)
    print("Testing Email Sender...")
    print("=" * 50)
    
    try:
        from outreach.email_sender import email_sender
        
        if not email_sender.is_configured():
            print("✗ Email Sender: Not configured")
            print("  Please set RESEND_API_KEY and SENDER_EMAIL in .env")
            return False
        
        stats = email_sender.get_email_stats()
        print(f"✓ Email Sender: Configured")
        print(f"  Sender: {stats['sender_name']} <{stats['sender_email']}>")
        print(f"  Quota: {stats['emails_sent_today']}/{stats['max_per_day']} today")
        return True
        
    except Exception as e:
        print(f"✗ Email Sender: FAILED - {str(e)}")
        return False
    
    finally:
        print()

def test_notion_crm():
    """Test Notion CRM configuration."""
    print("=" * 50)
    print("Testing Notion CRM...")
    print("=" * 50)
    
    try:
        from outreach.notion_crm import notion_crm
        
        if not notion_crm.is_configured():
            print("⚠ Notion CRM: Not configured (optional)")
            print("  Set NOTION_API_KEY and NOTION_DATABASE_ID to enable")
            return True  # Not required
        
        print(f"✓ Notion CRM: Configured")
        return True
        
    except Exception as e:
        print(f"✗ Notion CRM: FAILED - {str(e)}")
        return False
    
    finally:
        print()

def test_sample_workflow():
    """Test workflow with sample data."""
    print("=" * 50)
    print("Testing Sample Workflow...")
    print("=" * 50)
    
    # Check if sample leads file exists
    sample_file = "data/output/leads_UGC agencies_pune_20251105_172006.json"
    
    if not os.path.exists(sample_file):
        print(f"⚠ Sample file not found: {sample_file}")
        print("  Run the lead scraper first to generate sample data")
        return True  # Not a failure
    
    try:
        import json
        try:
            from agents.lead_agent import LeadOutreachAgent
        except ImportError:
            # Use simplified agent if LangChain has issues
            from agents.simple_agent import SimpleLeadAgent as LeadOutreachAgent
        
        # Load sample leads
        with open(sample_file, 'r') as f:
            leads = json.load(f)
        
        print(f"✓ Loaded {len(leads)} sample leads")
        
        # Test with first lead only
        if leads:
            test_lead = leads[0].copy()
            print(f"\nTesting with: {test_lead.get('business_name', 'Unknown')}")
            
            # Initialize agent
            agent = LeadOutreachAgent()
            print("✓ Agent initialized")
            
            # Test research (without email/generation)
            print("\nRunning AI research (this may take 30-60 seconds)...")
            result = agent.process_single_lead(
                test_lead,
                find_email=True,
                do_research=True,
                generate_email=False  # Skip email generation in test
            )
            
            print("\nResearch Results:")
            print(f"  Quality Score: {result.get('quality_score', 0)}/100")
            print(f"  Emails Found: {len(result.get('emails', []))}")
            print(f"  Research Status: {result.get('research_status', 'N/A')}")
            
            if result.get('business_summary'):
                print(f"  Summary: {result['business_summary'][:100]}...")
            
            print("\n✓ Sample workflow completed successfully")
            return True
        else:
            print("✗ No leads in sample file")
            return False
            
    except Exception as e:
        print(f"✗ Sample workflow: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print()

def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("AI LEAD OUTREACH AGENT - SYSTEM TEST")
    print("=" * 50 + "\n")
    
    results = {
        'Configuration': test_configuration(),
        'Imports': test_imports(),
        'AI Connection': test_ai_connection(),
        'Email Sender': test_email_sender(),
        'Notion CRM': test_notion_crm(),
        'Sample Workflow': test_sample_workflow(),
    }
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run: streamlit run app.py")
        print("2. Go to 'AI Outreach' tab")
        print("3. Import your leads and start the AI workflow")
    elif results['Configuration'] and results['Imports'] and results['AI Connection']:
        print("\n⚠ Core components working. Configure optional services:")
        if not results['Email Sender']:
            print("  - Set up Resend API for email sending")
        if not results['Notion CRM']:
            print("  - Set up Notion API for CRM tracking (optional)")
    else:
        print("\n❌ Critical tests failed. Please fix configuration:")
        if not results['Configuration']:
            print("  - Add API keys to .env file")
        if not results['Imports']:
            print("  - Install missing dependencies")
        if not results['AI Connection']:
            print("  - Verify Gemini API key")
    
    print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    main()

