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
    
    # Login form directly on home page
    st.markdown("### 🔐 Login to Access Dashboard")
    
    tab1, tab2 = st.tabs(["Request OTP", "Verify OTP"])
    
    with tab1:
        st.info("Enter your name to receive an OTP code")
        username = st.text_input("Username (your full name)", placeholder="Dhany Arya Pratama", key="home_username")
        if st.button("🚀 Send OTP", type="primary", key="home_send_otp"):
            if not username:
                st.error("Please enter your username.")
            else:
                try:
                    import httpx
                    from app.config import settings
                    API_URL = settings.fastapi_base_url
                    
                    resp = httpx.post(
                        f"{API_URL}/api/v1/auth/login",
                        json={"username": username},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["login_username"] = username
                        st.success(f"✅ {data.get('message', 'OTP sent!')}")
                        if "otp" in data:  # debug mode
                            st.code(f"DEBUG OTP: {data['otp']}")
                            st.info("👉 Copy the OTP code above and paste it in the 'Verify OTP' tab")
                    else:
                        st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    st.info("Make sure FastAPI backend is running on http://localhost:8000")
    
    with tab2:
        st.info("Enter the OTP code you received")
        user = st.text_input("Username", value=st.session_state.get("login_username", ""), key="home_verify_user")
        otp_code = st.text_input("OTP Code", max_chars=6, placeholder="123456", key="home_otp_code")
        if st.button("✅ Verify OTP", type="primary", key="home_verify_otp"):
            if not user or not otp_code:
                st.error("Please fill in both fields.")
            else:
                try:
                    import httpx
                    from app.config import settings
                    API_URL = settings.fastapi_base_url
                    
                    resp = httpx.post(
                        f"{API_URL}/api/v1/auth/verify-otp",
                        json={"username": user, "otp_code": otp_code},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["refresh_token"] = data["refresh_token"]
                        st.success("🎉 Login successful! Reloading dashboard...")
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.json().get('detail', 'Invalid OTP')}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
    
    st.divider()
    
    # Features list
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        **Features:**
        - 🔍 Browse scraped jobs
        - 🤖 AI-powered job matching
        - 📊 Score dashboard & analytics
        - ✉️ Auto-generated cover letters
        - 📱 Telegram notifications
        """)
    
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
