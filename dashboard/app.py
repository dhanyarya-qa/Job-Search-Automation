"""
Streamlit Dashboard — Main entry point.
Ultimate Job Hunting ATS — Command Center
"""

from __future__ import annotations

import os

import streamlit as st

st.set_page_config(
    page_title="Ultimate Job Hunting ATS",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #16213e;
        color: white;
    }

    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
    }

    .score-elite { background: #00b09b; color: white; }
    .score-good { background: #2196F3; color: white; }
    .score-average { background: #FF9800; color: white; }
    .score-low { background: #f44336; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─── Check Session ────────────────────────────────────────────────
if "access_token" not in st.session_state:
    st.markdown(
        """
        <div class="main-header">
            <h1>🎯 Ultimate Job Hunting ATS</h1>
            <p>Enterprise AI-Powered Job Hunting Command Center</p>
            <p><em>by Dhany Arya Pratama</em></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning("⚠️ Please login via the **Login** page in the sidebar.")
    st.stop()


# ─── Authenticated Home ───────────────────────────────────────────
st.markdown(
    """
    <div class="main-header">
        <h1>🎯 Ultimate Job Hunting ATS</h1>
        <p>Enterprise AI-Powered Recruitment War Machine</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Jobs Scraped", st.session_state.get("total_jobs", 0), delta="+12 today")
with col2:
    st.metric("High Matches (90+)", st.session_state.get("elite_matches", 0), delta="+3")
with col3:
    st.metric("Applications Sent", st.session_state.get("applications", 0))
with col4:
    st.metric("Avg AI Score", f"{st.session_state.get('avg_score', 0):.1f}/100")

st.divider()
st.info("🚀 Navigate using the sidebar to explore jobs, AI scores, cover letters, and more.")
