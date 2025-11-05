"""Lead Scraper Dashboard - Main UI Application."""
import os
import time
import random
import json
import streamlit as st
import pandas as pd
from typing import List, Dict
from controllers.main_controller import LeadController
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

def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Lead Scraper",
        page_icon="🎯",
        layout="wide"
    )
    
    initialize_session_state()
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