"""
Cover Letter Viewer Page — View and copy generated cover letters.
"""

from __future__ import annotations

import httpx
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(page_title="Cover Letter Viewer | ATS", page_icon="✉️", layout="wide")
st.markdown("## ✉️ Cover Letter Viewer")
st.caption("AI-generated hyper-personalized cover letters")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔍 Find by Job")
    keyword = st.text_input("Search job title or company", placeholder="e.g. Playwright Corp")
    min_score = st.slider("Min AI Score", 0, 100, 70)
    search_btn = st.button("🔍 Search", type="primary")

    if search_btn:
        try:
            resp = httpx.get(
                f"{API_URL}/api/v1/ai-analysis/top-matches",
                params={"min_score": min_score, "limit": 20},
                headers=headers,
                timeout=15,
            )
            if resp.status_code == 200:
                matches = resp.json()["results"]
                st.session_state["cover_letter_matches"] = matches
                st.success(f"Found {len(matches)} matches")
            else:
                st.error("Failed to fetch matches")
        except Exception as e:
            st.error(f"Error: {e}")

    if "cover_letter_matches" in st.session_state:
        matches = st.session_state["cover_letter_matches"]
        for i, m in enumerate(matches):
            label = f"Score: {m['match_score']:.0f} | {m['job_category']}"
            if st.button(label, key=f"cl_select_{i}"):
                st.session_state["selected_analysis_id"] = m["id"]
                st.session_state["selected_job_id"] = m["job_id"]

with col2:
    st.subheader("📝 Cover Letter")

    if "selected_job_id" in st.session_state:
        try:
            # Fetch job details
            job_resp = httpx.get(
                f"{API_URL}/api/v1/jobs/{st.session_state['selected_job_id']}",
                headers=headers,
                timeout=10,
            )
            if job_resp.status_code == 200:
                job = job_resp.json()
                st.markdown(f"**{job['job_title']}** @ {job['company_name']}")
                st.caption(f"Platform: {job['source_platform']} | Location: {job.get('location', 'N/A')}")
                st.divider()

            # Generate cover letter on demand
            generate = st.button("🤖 Generate / Regenerate Cover Letter", type="primary")
            if generate:
                with st.spinner("Generating personalized cover letter..."):
                    ai_resp = httpx.post(
                        f"{API_URL}/api/v1/ai-analysis/analyze",
                        json={
                            "job_id": st.session_state["selected_job_id"],
                            "generate_cover_letter": True,
                            "generate_interview_prep": False,
                        },
                        headers=headers,
                        timeout=90,
                    )
                    if ai_resp.status_code == 200:
                        result = ai_resp.json()
                        st.session_state["current_cover_letter"] = result.get("cover_letter", "")
                        st.session_state["current_score"] = result.get("match_score", 0)
                        st.session_state["current_prediction"] = result.get("prediction_market", "")
                    else:
                        st.error("Failed to generate cover letter")

            if "current_cover_letter" in st.session_state and st.session_state["current_cover_letter"]:
                score = st.session_state.get("current_score", 0)
                prediction = st.session_state.get("current_prediction", "")

                score_color = "#00b09b" if score >= 90 else "#2196F3" if score >= 75 else "#FF9800"
                st.markdown(
                    f'<div style="background:{score_color};color:white;padding:8px 16px;'
                    f'border-radius:8px;display:inline-block;font-weight:700;">'
                    f'Score: {score:.0f}/100 — {prediction}</div>',
                    unsafe_allow_html=True,
                )
                st.divider()

                cover_letter = st.session_state["current_cover_letter"]
                st.text_area(
                    "Generated Cover Letter",
                    value=cover_letter,
                    height=400,
                    key="cover_letter_text",
                )
                st.button("📋 Copy to Clipboard", help="Select all text above and copy manually")

                word_count = len(cover_letter.split())
                char_count = len(cover_letter)
                st.caption(f"📊 {word_count} words | {char_count} characters")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("👈 Search and select a job to view or generate its cover letter.")
