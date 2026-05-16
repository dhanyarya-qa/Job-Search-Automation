"""
Job Explorer Page — Browse, filter, and search scraped jobs.
"""

from __future__ import annotations

import httpx
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(page_title="Job Explorer | ATS", page_icon="🔍", layout="wide")
st.markdown("## 🔍 Job Explorer")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# ─── Filters ──────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    keyword = st.text_input("🔎 Search keyword", placeholder="QA Automation...")
with col2:
    platform = st.selectbox("Platform", ["All", "linkedin", "jobstreet", "glints", "kalibrr", "cryptojobslist"])
with col3:
    page = st.number_input("Page", min_value=1, value=1)

if st.button("🔍 Search Jobs", type="primary"):
    params: dict = {"page": page, "page_size": 20}
    if keyword:
        params["keyword"] = keyword
    if platform != "All":
        params["platform"] = platform

    try:
        resp = httpx.get(f"{API_URL}/api/v1/jobs/", params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            st.markdown(f"### Found **{data['total']}** jobs")
            for job in data["results"]:
                with st.expander(f"📋 {job['job_title']} — {job['company_name']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Platform:** {job['source_platform']}")
                        st.write(f"**Location:** {job.get('location', 'N/A')}")
                    with col_b:
                        st.write(f"**Salary:** {job.get('salary') or 'N/A'}")
                        st.write(f"**Posted:** {job['created_at'][:10]}")
                    st.link_button("🔗 View Job", job["job_url"])
                    if st.button(f"🤖 AI Analyze", key=f"analyze_{job['id']}"):
                        with st.spinner("Running AI analysis..."):
                            ai_resp = httpx.post(
                                f"{API_URL}/api/v1/ai-analysis/analyze",
                                json={"job_id": job["id"]},
                                headers=headers,
                                timeout=60,
                            )
                            if ai_resp.status_code == 200:
                                ai = ai_resp.json()
                                st.success(f"✅ Match Score: **{ai['match_score']:.0f}/100** — {ai['prediction_market']}")
                                st.write(ai["reasoning"])
                            else:
                                st.error("AI analysis failed")
        else:
            st.error(f"API error: {resp.status_code}")
    except Exception as e:
        st.error(f"Error: {e}")
