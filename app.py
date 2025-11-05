"""Lead Scraper Dashboard - Main UI Application."""
import os
import time
import random
import json
import streamlit as st
import pandas as pd
from typing import List, Dict
from controllers.main_controller import LeadController
from agents.orchestrator import OutreachOrchestrator
from outreach.email_sender import email_sender
from outreach.notion_crm import notion_crm
from utils.logger import setup_logger

logger = setup_logger(__name__)

def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'scraping_in_progress' not in st.session_state:
        st.session_state.scraping_in_progress = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'live_data' not in st.session_state:
        st.session_state.live_data = []
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    
    # AI Outreach state
    if 'outreach_leads' not in st.session_state:
        st.session_state.outreach_leads = []
    if 'outreach_in_progress' not in st.session_state:
        st.session_state.outreach_in_progress = False
    if 'outreach_logs' not in st.session_state:
        st.session_state.outreach_logs = []
    if 'workflow_stats' not in st.session_state:
        st.session_state.workflow_stats = None

def setup_ui() -> tuple[str, str, List[str], str, int]:
    """
    Setup the UI components and return user inputs.
    
    Returns:
        tuple containing keyword, location, selected platforms, mode, and max_leads
    """
    st.title("Lead Scraper Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Input fields
        keyword = st.text_input("Business Type", placeholder="e.g., Cafe")
        location = st.text_input("Location", placeholder="e.g., New York, NY")
        
        # Add extraction limit option as text input
        max_leads = st.number_input(
            "Maximum Leads to Extract",
            min_value=1,
            value=15,
            help="Limit the number of leads to extract to avoid long processing times"
        )
    
    with col2:
        # Platform selection
        platforms = st.multiselect(
            "Select Platforms",
            ["Google Maps", "Website Scraper"],
            default=["Google Maps"]
        )
        
        # Mode selection
        mode = st.radio(
            "Scraping Mode",
            ["Contacts Only", "Full Data"],
            index=1,
            help="Full Data includes website analysis and social media links"
        )
    
    return keyword, location, platforms, mode, max_leads

def update_live_data(lead):
    """Update the live data in session state."""
    if lead:
        st.session_state.live_data.append(lead)

def display_live_data():
    """Display the leads being collected in real-time."""
    if not st.session_state.live_data:
        return
    
    st.subheader("📊 Live Data Collection")
    
    # Convert the list of leads to a DataFrame
    live_df = pd.DataFrame(st.session_state.live_data)
    
    # Display as a table that updates
    st.dataframe(live_df, use_container_width=True)
    
    # Show count of leads collected
    st.caption(f"Collected {len(st.session_state.live_data)} leads so far...")

def display_log_messages():
    """Display log messages in the UI."""
    if not st.session_state.log_messages:
        return
    
    with st.expander("📋 Scraping Logs", expanded=False):
        for msg in st.session_state.log_messages:
            st.text(msg)

def add_log_message(message):
    """Add a log message to the session state."""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.log_messages.append(f"[{timestamp}] {message}")

def display_results(results):
    """Display the scraping results and download options."""
    if not results or not results.get('leads') or not results.get('export_paths'):
        return
    
    leads = results.get('leads', [])
    export_paths = results.get('export_paths', {})
    
    if not leads:
        st.warning("No leads found. Try changing your search criteria.")
        return
    
    st.success(f"✅ Successfully found {len(leads)} leads!")
    
    # Add unique identifiers to keys to avoid duplication
    unique_id = f"{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Data Table", "📋 Detailed View", "💾 Export Options"])
    
    with tab1:
        # Display leads as a table
        lead_df = pd.DataFrame(leads)
        st.dataframe(lead_df, use_container_width=True)
    
    with tab2:
        # Create expandable sections for each lead with detailed view
        for i, lead in enumerate(leads):
            # Create a unique key for each expander based on position and business name
            expander_label = f"{i+1}. {lead.get('business_name', 'Unnamed business')}"
            
            # Remove the key parameter which isn't supported in Streamlit 1.22.0
            with st.expander(expander_label):
                cols = st.columns(2)
                with cols[0]:
                    st.markdown(f"**Business Name:** {lead.get('business_name', 'N/A')}")
                    st.markdown(f"**Phone:** {lead.get('phone', 'N/A')}")
                    st.markdown(f"**Website:** [{lead.get('website', 'N/A')}]({lead.get('website', '#')})" if lead.get('website') else "**Website:** N/A")
                with cols[1]:
                    st.markdown(f"**Address:** {lead.get('address', 'N/A')}")
                    st.markdown(f"**Rating:** {lead.get('rating', 'N/A')}")
                    
                    if "emails" in lead and lead["emails"]:
                        st.markdown(f"**Emails:** {', '.join(lead['emails'])}")
                    
                    if "social_links" in lead and lead["social_links"]:
                        st.markdown("**Social Links:**")
                        for platform, url in lead["social_links"].items():
                            st.markdown(f"- {platform}: [{url}]({url})")
                    
                    st.markdown(f"**Notes:** {lead.get('notes', '')}")
    
    with tab3:
        # Download buttons - fix the duplicate ID issue by ensuring each button has a unique key
        col1, col2, col3 = st.columns(3)
        
        # Generate truly unique IDs for each button based on the timestamp, random number and button type
        csv_key = f"csv_{unique_id}"
        excel_key = f"excel_{unique_id}"
        json_key = f"json_{unique_id}"
        
        with col1:
            if export_paths.get('csv'):
                with open(export_paths['csv'], 'rb') as f:
                    st.download_button(
                        label="Download CSV",
                        data=f,
                        file_name=os.path.basename(export_paths['csv']),
                        mime="text/csv",
                        key=csv_key
                    )
        
        with col2:
            if export_paths.get('xlsx'):
                with open(export_paths['xlsx'], 'rb') as f:
                    st.download_button(
                        label="Download Excel",
                        data=f,
                        file_name=os.path.basename(export_paths['xlsx']),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=excel_key
                    )
        
        with col3:
            # Add JSON export option
            if export_paths.get('json'):
                with open(export_paths['json'], 'rb') as f:
                    st.download_button(
                        label="Download JSON",
                        data=f,
                        file_name=os.path.basename(export_paths['json']),
                        mime="application/json",
                        key=json_key
                    )
            # Fallback if json path doesn't exist but we have leads
            elif leads:
                json_data = json.dumps(leads, indent=2, default=str)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"leads_{results.get('keyword', 'data')}_{results.get('location', 'export')}_{time.strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=json_key
                )

def render_ai_outreach_tab():
    """Render the AI Outreach Agent tab."""
    st.header("🤖 AI Outreach Agent")
    
    # Configuration section
    with st.expander("⚙️ Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**API Status**")
            gemini_key = os.getenv('GEMINI_API_KEY', 'Not set')
            resend_key = os.getenv('RESEND_API_KEY', 'Not set')
            notion_key = os.getenv('NOTION_API_KEY', 'Not set')
            
            st.text(f"Gemini API: {'✓' if gemini_key != 'Not set' and gemini_key != 'your_gemini_api_key_here' else '✗'}")
            st.text(f"Resend API: {'✓' if resend_key != 'Not set' and resend_key != 'your_resend_api_key_here' else '✗'}")
            st.text(f"Notion API: {'✓' if notion_key != 'Not set' and notion_key != 'your_notion_integration_key_here' else '✗'}")
        
        with col2:
            st.write("**Email Stats**")
            if email_sender.is_configured():
                stats = email_sender.get_email_stats()
                st.text(f"Sent Today: {stats['emails_sent_today']}/{stats['max_per_day']}")
                st.text(f"Remaining: {stats['remaining_today']}")
            else:
                st.warning("Email sender not configured")
    
    # Lead import section
    st.subheader("1️⃣ Import Leads")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload JSON file with leads",
            type=['json'],
            help="Upload a JSON file from previous scraping sessions"
        )
        
        if uploaded_file:
            try:
                leads_data = json.load(uploaded_file)
                st.success(f"Loaded {len(leads_data)} leads from file")
                if st.button("Import These Leads"):
                    st.session_state.outreach_leads = leads_data
                    st.session_state.workflow_stats = None
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to load file: {str(e)}")
    
    with col2:
        # Or use recent scrapes
        st.write("**Or use recent scrapes:**")
        output_dir = "data/output"
        if os.path.exists(output_dir):
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            if json_files:
                selected_file = st.selectbox("Recent files", json_files)
                if st.button("Load Selected"):
                    try:
                        with open(os.path.join(output_dir, selected_file), 'r') as f:
                            leads_data = json.load(f)
                        st.session_state.outreach_leads = leads_data
                        st.session_state.workflow_stats = None
                        st.success(f"Loaded {len(leads_data)} leads")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to load: {str(e)}")
    
    # Show loaded leads
    if st.session_state.outreach_leads:
        st.info(f"📊 {len(st.session_state.outreach_leads)} leads loaded")
        
        # Workflow controls
        st.subheader("2️⃣ AI Workflow")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            auto_approve_score = st.number_input(
                "Auto-approve threshold",
                min_value=0,
                max_value=100,
                value=80,
                help="Automatically approve leads with quality score above this"
            )
        
        with col2:
            send_immediately = st.checkbox(
                "Send emails immediately",
                value=False,
                help="Send approved emails immediately (otherwise manual review)"
            )
        
        with col3:
            sync_notion = st.checkbox(
                "Sync to Notion",
                value=True,
                help="Sync leads to Notion CRM"
            )
        
        # Run workflow button
        if st.button("🚀 Run AI Workflow", type="primary", disabled=st.session_state.outreach_in_progress):
            st.session_state.outreach_in_progress = True
            st.session_state.outreach_logs = []
            
            # Create orchestrator with callbacks
            def on_status(msg):
                st.session_state.outreach_logs.append(msg)
            
            orchestrator = OutreachOrchestrator(on_status_update=on_status)
            
            # Save leads to temp file
            temp_file = "data/output/temp_outreach.json"
            with open(temp_file, 'w') as f:
                json.dump(st.session_state.outreach_leads, f)
            
            # Run workflow
            with st.spinner("Running AI workflow..."):
                result = orchestrator.run_complete_workflow(
                    temp_file,
                    auto_approve_threshold=auto_approve_score if auto_approve_score > 0 else None,
                    send_emails=send_immediately
                )
            
            st.session_state.outreach_leads = result['leads']
            st.session_state.workflow_stats = result['stats']
            st.session_state.outreach_in_progress = False
            st.rerun()
        
        # Display logs
        if st.session_state.outreach_logs:
            with st.expander("📋 Workflow Logs", expanded=True):
                for log in st.session_state.outreach_logs:
                    st.text(log)
        
        # Display workflow stats
        if st.session_state.workflow_stats:
            st.subheader("📊 Workflow Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            stats = st.session_state.workflow_stats
            
            with col1:
                st.metric("Total Leads", stats['total_leads'])
                st.metric("Researched", stats['researched'])
            
            with col2:
                st.metric("Qualified", stats['qualified'])
                st.metric("Not Qualified", stats['total_leads'] - stats['qualified'])
            
            with col3:
                st.metric("Emails Generated", stats['emails_generated'])
                st.metric("Approved", stats['approved'])
            
            with col4:
                st.metric("Sent", stats['sent'])
                st.metric("Notion Synced", stats['synced_to_notion'])
        
        # Lead review section
        st.subheader("3️⃣ Review & Approve Emails")
        
        # Filter options
        filter_option = st.radio(
            "Show",
            ["All Leads", "Awaiting Approval", "Qualified Only", "Sent"],
            horizontal=True
        )
        
        # Filter leads based on selection
        display_leads = st.session_state.outreach_leads
        if filter_option == "Awaiting Approval":
            display_leads = [l for l in display_leads if l.get('email_status') == 'generated' and not l.get('email_approved')]
        elif filter_option == "Qualified Only":
            display_leads = [l for l in display_leads if l.get('quality_score', 0) >= 60]
        elif filter_option == "Sent":
            display_leads = [l for l in display_leads if l.get('email_sent')]
        
        st.write(f"Showing {len(display_leads)} leads")
        
        # Display leads for review
        for i, lead in enumerate(display_leads):
            with st.expander(
                f"{'✅' if lead.get('email_approved') else '⏳'} {lead.get('business_name', 'Unknown')} "
                f"(Score: {lead.get('quality_score', 0)})"
            ):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Business Information**")
                    st.text(f"Website: {lead.get('website', 'N/A')}")
                    st.text(f"Phone: {lead.get('phone', 'N/A')}")
                    st.text(f"Emails: {', '.join(lead.get('emails', ['None']))}")
                    
                    if lead.get('business_summary'):
                        st.write("**AI Research Summary**")
                        st.info(lead['business_summary'])
                    
                    if lead.get('pain_points'):
                        st.write("**Pain Points**")
                        for pp in lead['pain_points'][:3]:
                            st.text(f"• {pp}")
                
                with col2:
                    st.write("**Status**")
                    st.text(f"Quality: {lead.get('quality_score', 0)}/100")
                    st.text(f"Email Status: {lead.get('email_status', 'N/A')}")
                    if lead.get('email_approved'):
                        st.success("✅ Approved")
                    if lead.get('email_sent'):
                        st.success(f"✉️ Sent at {lead.get('email_sent_at', 'N/A')[:19]}")
                
                # Show generated email
                if lead.get('email_subject') and lead.get('email_body'):
                    st.write("**Generated Email**")
                    st.text_input(f"Subject {i}", value=lead['email_subject'], key=f"subj_{i}", disabled=True)
                    st.text_area(f"Body {i}", value=lead['email_body'], height=200, key=f"body_{i}", disabled=True)
                    
                    # Approval buttons
                    if not lead.get('email_approved') and not lead.get('email_sent'):
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Approve", key=f"approve_{i}"):
                                lead['email_approved'] = True
                                st.success("Approved!")
                                st.rerun()
                        with col2:
                            if st.button(f"❌ Reject", key=f"reject_{i}"):
                                lead['email_approved'] = False
                                lead['email_rejected'] = True
                                st.rerun()
    
    else:
        st.info("👆 Import leads to begin the AI outreach workflow")

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Lead Scraper & AI Outreach",
        page_icon="🎯",
        layout="wide"
    )
    
    initialize_session_state()
    
    # Create tabs
    tab1, tab2 = st.tabs(["🔍 Lead Scraper", "🤖 AI Outreach"])
    
    with tab1:
        render_lead_scraper_tab()
    
    with tab2:
        render_ai_outreach_tab()

def render_lead_scraper_tab():
    """Render the original lead scraper tab."""
    st.title("Lead Scraper Dashboard")
    
    keyword, location, platforms, mode, max_leads = setup_ui()
    
    # Create columns for buttons
    col1, col2 = st.columns(2)
    
    # Status/Progress area
    status_container = st.empty()
    progress_bar = st.progress(0)
    log_area = st.container()
    
    with col1:
        start_button = st.button(
            "Start Scraping",
            type="primary",
            disabled=st.session_state.scraping_in_progress
        )
    
    with col2:
        if st.button("Clear Results"):
            st.session_state.results = None
            st.session_state.live_data = []
            st.session_state.log_messages = []
            st.experimental_rerun()
    
    # Live data display area (will update during scraping)
    live_data_container = st.container()
    
    try:
        if start_button and not st.session_state.scraping_in_progress:
            if not keyword or not location:
                st.error("Please enter both business type and location")
                return
            
            if not platforms:
                st.error("Please select at least one platform")
                return
            
            # Reset live data and logs
            st.session_state.live_data = []
            st.session_state.log_messages = []
            st.session_state.scraping_in_progress = True
            status_container.info("🔄 Scraping in progress...")
            
            # Initialize controller with callbacks for live updates
            controller = LeadController(
                on_lead_extracted=update_live_data,
                on_log_message=add_log_message,
                max_leads=max_leads
            )
            
            try:
                # Run scraping in a way that allows UI updates
                progress_placeholder = st.empty()
                
                # This will be updated by the controller during scraping
                with live_data_container:
                    display_live_data()
                
                # Execute the scraping
                results = controller.run(keyword, location, platforms, mode)
                
                # Add the keyword and location to the results for use in export names
                results['keyword'] = keyword
                results['location'] = location
                
                # Store results in session state
                st.session_state.results = results
                
                # Clear progress indicators
                status_container.empty()
                progress_bar.empty()
                
                # Display final results
                display_results(results)
                
            except Exception as e:
                st.error(f"❌ Error during scraping: {str(e)}")
                logger.error(f"Scraping failed: {str(e)}", exc_info=True)
            
            finally:
                st.session_state.scraping_in_progress = False
                
                # Display log messages
                with log_area:
                    display_log_messages()
    
    except Exception as e:
        st.error(f"❌ Application error: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)
    
    # Display previous results if they exist
    if st.session_state.results:
        display_results(st.session_state.results)
    
    # Always show live data and logs if they exist
    with live_data_container:
        display_live_data()
    
    with log_area:
        display_log_messages()

if __name__ == "__main__":
    main()