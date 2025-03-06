import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, List
import time

# Configure page
st.set_page_config(
    page_title="Google Maps Scraper",
    page_icon="🗺️",
    layout="wide"
)

# Constants
API_URL = "http://localhost:8000"
DEFAULT_QUERY = "paper cup manufactures in jaipur"

def search_places(query: str, progress_bar) -> Dict:
    """Send search query to FastAPI backend and return results with progress updates"""
    try:
        # Initialize progress
        progress_bar.progress(0, "Initializing scraper...")
        time.sleep(0.5)
        
        # Make the API request
        progress_bar.progress(20, "Connecting to Google Maps...")
        response = requests.post(
            f"{API_URL}/scrape",
            json={"query": query}
        )
        response.raise_for_status()
        
        # Update progress based on response
        results = response.json()
        if results and results.get('total_results', 0) > 0:
            progress_bar.progress(100, "✅ Scraping completed!")
        else:
            progress_bar.progress(100, "No results found")
            
        return results
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        progress_bar.progress(100, "❌ Error occurred")
        return None

def display_results(data: Dict) -> None:
    """Display scraped results in a nice format"""
    if not data:
        return

    st.subheader(f"Found {data['total_results']} locations")

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Table View", "📝 Detailed View"])
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(data['locations'])
    
    with tab1:
        # Show interactive table with loading animation
        with st.spinner("Loading data table..."):
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        
        # Download section
        st.write("---")
        st.write("📥 **Download Options**")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download CSV",
                csv,
                "google_maps_data.csv",
                "text/csv",
                key='download-csv',
                help="Download the data as CSV file"
            )
        
        with col2:
            json_str = df.to_json(orient='records')
            st.download_button(
                "📋 Download JSON",
                json_str,
                "google_maps_data.json",
                "application/json",
                key='download-json',
                help="Download the data as JSON file"
            )

    with tab2:
        # Detailed cards view with loading animation
        with st.spinner("Loading detailed views..."):
            for loc in data['locations']:
                with st.expander(f"📍 {loc['name']} - {loc['address']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Category:**", loc['category'])
                        st.write("**Rating:**", loc['rating'])
                        st.write("**Reviews:**", loc['total_reviews'])
                        st.write("**Status:**", loc['business_status'])
                        if loc['website']:
                            st.write("**Website:**", f"[Link]({loc['website']})")
                    
                    with col2:
                        st.write("**Phone:**", loc['phone'])
                        st.write("**Email:**", loc['email'])
                        st.write("**Hours:**", loc['hours'])
                        if loc['google_maps_url']:
                            st.write("**Maps Link:**", f"[Open in Google Maps]({loc['google_maps_url']})")

def main():
    # Header
    st.title("🗺️ Google Maps Scraper")
    st.markdown("""
    Enter a search query to scrape business information from Google Maps.
    Example: "restaurants in new york" or "hotels in paris"
    """)

    # Search form
    with st.form(key="search_form"):
        query = st.text_input(
            "Search Query",
            value=DEFAULT_QUERY,
            help="Enter what you want to search for on Google Maps"
        )
        submit_button = st.form_submit_button("🔎 Search")

    # Create a placeholder for the progress bar
    progress_placeholder = st.empty()

    # Handle form submission
    if submit_button:
        if not query:
            st.warning("Please enter a search query")
        else:
            # Create a progress bar
            progress_bar = progress_placeholder.progress(0)
            
            # Show progress status
            status_text = st.empty()
            
            with st.spinner():
                results = search_places(query, progress_bar)
                if results:
                    display_results(results)
            
            # Clear the progress bar after completion
            progress_placeholder.empty()

if __name__ == "__main__":
    main()