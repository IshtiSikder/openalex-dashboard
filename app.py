import streamlit as st
import pandas as pd
import plotly.express as px
from pyalex import Works, config
import time
import os
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv
from streamlit_supabase_auth import login_form, logout_button
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Configure PyAlex
# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Rate limiting configuration
RATE_LIMIT = 10  # requests per minute
RATE_WINDOW = 60  # seconds

def get_client_ip():
    """
    Get client identifier for rate limiting.
    Uses authenticated user ID if available, else session hash.
    """
    if "user" in st.session_state and st.session_state.user:
        user_id = st.session_state.user.get('id', '')
        return hashlib.md5(user_id.encode()).hexdigest()[:15]

    try:
        if "client_ip" not in st.session_state:
            session_id = str(id(st.session_state))
            st.session_state.client_ip = hashlib.md5(session_id.encode()).hexdigest()[:15]
        return st.session_state.client_ip
    except Exception:
        return "local"

def check_rate_limit():
    """
    Check if current request exceeds rate limits.
    Uses st.session_state to persist history across Streamlit reruns.
    Returns: (allowed: bool, remaining: int, wait_time: int)
    """
    # Initialize request history in session state if not exists
    if "request_history" not in st.session_state:
        st.session_state.request_history = []

    now = datetime.now()
    cutoff_time = now - timedelta(seconds=RATE_WINDOW)

    # Clean up old requests
    st.session_state.request_history = [
        req_time for req_time in st.session_state.request_history
        if req_time > cutoff_time
    ]

    # Count recent requests
    request_count = len(st.session_state.request_history)

    if request_count >= RATE_LIMIT:
        # Rate limit exceeded
        oldest = st.session_state.request_history[0]
        wait_seconds = int((oldest + timedelta(seconds=RATE_WINDOW) - now).total_seconds())
        return (False, 0, max(1, wait_seconds))

    # Allow request and record it
    st.session_state.request_history.append(now)
    return (True, RATE_LIMIT - request_count - 1, 0)

def check_authentication():
    """Display login form and return session if authenticated."""
    session = login_form(
        url=SUPABASE_URL,
        apiKey=SUPABASE_ANON_KEY,
        providers=["google", "github"],
    )
    return session

def get_user_email(session) -> str:
    """Extract user email from session for OpenAlex API."""
    if session and 'user' in session:
        return session['user'].get('email', '')
    return os.getenv("OPENALEX_EMAIL", "noreply@example.com")

# Page configuration
st.set_page_config(
    page_title="OpenAlex Research Dashboard",
    page_icon="📚",
    layout="wide"
)

# Authentication gate
session = check_authentication()
if not session:
    st.stop()

# Set PyAlex email from logged-in user
user_email = get_user_email(session)
config.email = user_email
st.session_state.user = session['user']

# Title
st.title("📚 OpenAlex Research Dashboard")
st.caption(f"Logged in as: {user_email}")

# Sidebar for filters
st.sidebar.header("Search & Filters")
if st.sidebar.button("Logout", type="secondary"):
    logout_button()
    st.rerun()
st.sidebar.divider()

# Search query input
search_query = st.sidebar.text_input(
    "Search Query",
    placeholder="Enter keywords, topics, or research terms...",
    help="Search for research papers by keywords"
)

# Year filter
year_range = st.sidebar.slider(
    "Publication Year Range",
    min_value=2000,
    max_value=2024,
    value=(2015, 2024),
    help="Filter papers by publication year"
)

# Number of results
num_results = st.sidebar.selectbox(
    "Number of Results",
    options=[10, 25, 50, 100],
    index=0,
    help="Maximum number of results to display"
)

# Search button
search_button = st.sidebar.button("🔍 Search", type="primary", use_container_width=True)

# Main content area
if search_button:
    # Check rate limit first
    is_allowed, remaining, wait_time = check_rate_limit()

    if not is_allowed:
        st.error(f"⚠️ Too many searches! Please wait {wait_time} seconds before trying again.\n\nRate limit: {RATE_LIMIT} searches per minute.")
    elif not search_query:
        st.warning("⚠️ Please enter a search query to continue.")
    else:
        try:
            # Show loading message
            with st.spinner(f"Searching OpenAlex for '{search_query}'..."):
                # Query OpenAlex API using PyAlex
                works = Works().search(search_query).filter(
                    publication_year=f"{year_range[0]}-{year_range[1]}"
                )

                # Fetch results
                results = []
                for work in works.get(per_page=num_results):
                    # Extract author names
                    authors = []
                    if work.get('authorships'):
                        authors = [
                            authorship['author']['display_name']
                            for authorship in work['authorships'][:3]  # First 3 authors
                            if authorship.get('author') and authorship['author'].get('display_name')
                        ]
                        if len(work['authorships']) > 3:
                            authors.append("et al.")

                    authors_str = ", ".join(authors) if authors else "Unknown"

                    # Get publication year
                    pub_year = work.get('publication_year', 'N/A')

                    # Get citation count
                    citation_count = work.get('cited_by_count', 0)

                    # Get title
                    title = work.get('title', 'Untitled')

                    # Get DOI
                    doi = work.get('doi', '')

                    results.append({
                        'Title': title,
                        'Authors': authors_str,
                        'Year': pub_year,
                        'Citations': citation_count,
                        'DOI': doi
                    })

                # Check if we got results
                if not results:
                    st.info(f"No results found for '{search_query}' in the selected year range.")
                else:
                    # Convert to DataFrame
                    df = pd.DataFrame(results)

                    # Display summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Results", len(df))
                    with col2:
                        st.metric("Total Citations", f"{df['Citations'].sum():,}")
                    with col3:
                        st.metric("Average Citations", f"{df['Citations'].mean():.1f}")
                    with col4:
                        st.metric("Year Range", f"{df['Year'].min()}-{df['Year'].max()}")

                    st.markdown("---")

                    # Display results table
                    st.subheader("📊 Search Results")

                    # Create a displayable dataframe with clickable DOIs
                    display_df = df.copy()
                    display_df = display_df[['Title', 'Authors', 'Year', 'Citations']]

                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400,
                        hide_index=True
                    )

                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"openalex_results_{search_query.replace(' ', '_')}.csv",
                        mime="text/csv",
                    )

                    st.markdown("---")

                    # Citations bar chart for top 10 results
                    st.subheader("📈 Top 10 Most Cited Papers")

                    # Sort by citations and get top 10
                    top_10 = df.nlargest(10, 'Citations')

                    # Create bar chart
                    fig = px.bar(
                        top_10,
                        x='Citations',
                        y='Title',
                        orientation='h',
                        title=f'Citation Count for Top 10 Results',
                        labels={'Citations': 'Number of Citations', 'Title': 'Paper Title'},
                        color='Citations',
                        color_continuous_scale='Blues',
                        height=500
                    )

                    # Update layout
                    fig.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        showlegend=False,
                        xaxis_title="Citations",
                        yaxis_title="",
                        font=dict(size=12)
                    )

                    # Truncate long titles in chart
                    fig.update_yaxes(ticktext=[
                        title[:60] + '...' if len(title) > 60 else title
                        for title in top_10['Title']
                    ], tickvals=list(range(len(top_10))))

                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ An error occurred while searching: {str(e)}")
            st.info("Please try again with a different query or check your internet connection.")

else:
    # Welcome message when no search has been performed
    st.info("👈 Enter a search query and click 'Search' to explore research papers from OpenAlex!")

    st.markdown("""
    ### About This Dashboard

    This dashboard allows you to:
    - 🔍 Search millions of research papers from the OpenAlex database
    - 📅 Filter results by publication year
    - 📊 View detailed information including authors, citations, and publication year
    - 📈 Visualize citation metrics for top papers
    - 💾 Download results as CSV for further analysis

    ### How to Use
    1. Enter your search query in the sidebar (e.g., "machine learning", "climate change")
    2. Adjust the publication year range if needed
    3. Select the number of results you want to see
    4. Click the "Search" button

    ### About OpenAlex
    [OpenAlex](https://openalex.org) is a fully open catalog of the global research system,
    providing free and open access to metadata for millions of scholarly works, authors, institutions, and more.
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
    Powered by <a href='https://openalex.org' target='_blank'>OpenAlex</a> |
    Built with <a href='https://streamlit.io' target='_blank'>Streamlit</a>
    </div>
    """,
    unsafe_allow_html=True
)
