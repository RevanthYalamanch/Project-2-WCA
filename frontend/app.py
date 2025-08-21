import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Configuration & State Management ---
st.set_page_config(page_title="Web Content Analyzer", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

# --- THE FIX IS HERE ---
# Use the 'backend' hostname when running inside Docker
# BACKEND_URL_ANALYZE = "http://backend:8000/analyze"
# BACKEND_URL_EXPORT = "http://backend:8000/export/pdf"

# Use the '127.0.0.1' address for local development (when not using Docker)
BACKEND_URL_ANALYZE = "http://127.0.0.1:8000/analyze"
BACKEND_URL_EXPORT = "http://127.0.0.1:8000/export/pdf"
# --- END OF FIX ---


# --- Helper Functions ---
def convert_to_csv(data: dict) -> str:
    """Flattens the JSON report and converts it to a CSV string."""
    df = pd.json_normalize(data)
    return df.to_csv(index=False).encode('utf-8')

def create_sentiment_chart(sentiment_data: dict):
    """Creates and displays a sentiment bar chart in Streamlit."""
    sentiment = sentiment_data.get('sentiment', 'neutral').lower()
    score_map = {'positive': 8.5, 'neutral': 5.0, 'negative': 2.0}
    score = score_map.get(sentiment, 5.0)
    color = 'forestgreen' if score > 6 else 'crimson' if score < 4 else 'gold'

    fig, ax = plt.subplots(figsize=(6, 1))
    ax.barh([0], [10], color='whitesmoke', height=0.5)
    ax.barh([0], [score], color=color, height=0.5)
    ax.set_xlim(0, 10)
    ax.set_yticks([])
    ax.set_xticks([])
    plt.box(False)
    st.pyplot(fig)

def display_report(report_data):
    """Renders a single, enhanced analysis report."""
    analysis = report_data.get('content_analysis', {})
    ai_summary = report_data.get('ai_summary', {})
    
    st.subheader(f"📄 Report for: {analysis.get('title', 'N/A')}")
    st.caption(f"URL: {report_data.get('url')}")
    st.markdown("---")

    st.markdown("### Executive Summary")
    st.write(ai_summary.get('summary', 'Not available.'))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Content Type", analysis.get('content_type', 'N/A'))
    with col2:
        st.metric("Sentiment", ai_summary.get('sentiment_analysis', {}).get('sentiment', 'N/A'))
    with col3:
        st.metric("Readability", ai_summary.get('readability', {}).get('score_description', 'N/A'))
    
    create_sentiment_chart(ai_summary.get('sentiment_analysis', {}))

    with st.expander("Key Points & Competitive Positioning"):
        st.markdown("#### Key Points")
        for point in ai_summary.get('key_points', []):
            st.markdown(f"- {point}")
        st.markdown("#### Competitive Positioning")
        st.write(ai_summary.get('competitive_positioning', 'Not available.'))

    with st.expander("SEO Analysis"):
        seo = ai_summary.get('seo_analysis', {})
        st.markdown("#### Recommendations")
        for rec in seo.get('recommendations', []):
            st.markdown(f"- {rec}")
        st.markdown("#### Target Keywords")
        st.write(", ".join(seo.get('target_keywords', [])))

    st.markdown("---")
    st.markdown("#### Export Report")
    c1, c2, c3 = st.columns(3)
    file_prefix = report_data.get('url').replace('https://', '').replace('http://', '').split('/')[0]
    
    with c1:
        st.download_button("Download as JSON", json.dumps(report_data, indent=2), f"report_{file_prefix}.json", "application/json")
    with c2:
        csv_data = convert_to_csv(report_data)
        st.download_button("Download as CSV", csv_data, f"report_{file_prefix}.csv", "text/csv")
    with c3:
        # For local run, we need the full URL for the backend service
        pdf_response = requests.post(BACKEND_URL_EXPORT, json=report_data)
        if pdf_response.status_code == 200:
            st.download_button("Download as PDF", pdf_response.content, f"report_{file_prefix}.pdf", "application/pdf")

# --- Main UI ---
st.title("🚀 Web Content Analyzer")

tab1, tab2 = st.tabs(["New Analysis", "Analysis History"])

with tab1:
    st.header("Analyze New Websites")
    urls_input = st.text_area("Enter URLs (one per line)", height=150, placeholder="https://www.google.com\nhttps://www.microsoft.com")
    analyze_button = st.button("Analyze Websites", type="primary")

    if analyze_button:
        urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
        if not urls:
            st.warning("Please enter at least one URL.")
        else:
            progress_bar = st.progress(0, "Initializing Batch Analysis...")
            for i, url in enumerate(urls):
                try:
                    progress_text = f"Analyzing ({i+1}/{len(urls)}): {url}"
                    progress_bar.progress((i / len(urls)), text=progress_text)
                    
                    payload = {"url": url}
                    response = requests.post(BACKEND_URL_ANALYZE, json=payload, timeout=180)

                    if response.status_code == 200:
                        st.success(f"Successfully analyzed {url}")
                        report_data = response.json()
                        st.session_state.history.append(report_data) # Add to history
                        display_report(report_data)
                    else:
                        st.error(f"Error analyzing {url}: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to connect to backend for {url}: {e}")
            progress_bar.progress(1.0, "Batch analysis complete!")

with tab2:
    st.header("Analysis History")
    if not st.session_state.history:
        st.info("No analyses in history. Run a new analysis to see results here.")
    else:
        for i, report_data in enumerate(reversed(st.session_state.history)):
            with st.expander(f"#{len(st.session_state.history)-i} - {report_data.get('content_analysis', {}).get('title', 'N/A')}"):
                display_report(report_data)