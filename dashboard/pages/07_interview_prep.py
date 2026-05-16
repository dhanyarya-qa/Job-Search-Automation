"""
Interview Prep Page — View AI-generated interview questions and model answers.
"""

from __future__ import annotations

import httpx
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(
    page_title="Interview Prep | ATS",
    page_icon="🎤",
    layout="wide",
)
st.markdown("## 🎤 Interview Preparation")
st.caption("AI-generated predicted interview questions with model answers")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🎯 Select Job")
    min_score = st.slider("Min Match Score", 0, 100, 70)

    if st.button("🔍 Load Top Matches", type="primary"):
        try:
            resp = httpx.get(
                f"{API_URL}/api/v1/ai-analysis/top-matches",
                params={"min_score": min_score, "limit": 15},
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                st.session_state["interview_matches"] = resp.json()["results"]
        except Exception as e:
            st.error(f"Error: {e}")

    if "interview_matches" in st.session_state:
        for i, m in enumerate(st.session_state["interview_matches"]):
            btn_label = f"🎯 Score {m['match_score']:.0f} | {m['job_category']}"
            if st.button(btn_label, key=f"iv_sel_{i}"):
                st.session_state["iv_job_id"] = m["job_id"]

with col2:
    st.subheader("❓ Interview Questions")

    if "iv_job_id" in st.session_state:
        if st.button("🤖 Generate Interview Prep", type="primary"):
            with st.spinner("Generating questions and model answers..."):
                try:
                    ai_resp = httpx.post(
                        f"{API_URL}/api/v1/ai-analysis/analyze",
                        json={
                            "job_id": st.session_state["iv_job_id"],
                            "generate_cover_letter": False,
                            "generate_interview_prep": True,
                        },
                        headers=headers,
                        timeout=90,
                    )
                    if ai_resp.status_code == 200:
                        result = ai_resp.json()
                        st.session_state["iv_questions"] = result.get("interview_questions", [])
                        st.session_state["iv_score"] = result.get("match_score", 0)
                    else:
                        st.error("Failed to generate questions")
                except Exception as e:
                    st.error(f"Error: {e}")

        if "iv_questions" in st.session_state:
            questions = st.session_state["iv_questions"]
            score = st.session_state.get("iv_score", 0)

            st.markdown(
                f'<span style="background:#667eea;color:white;padding:6px 14px;'
                f'border-radius:20px;font-weight:700;">Match Score: {score:.0f}/100</span>',
                unsafe_allow_html=True,
            )
            st.divider()

            if questions:
                for i, q in enumerate(questions, 1):
                    with st.expander(f"❓ Q{i}: {q[:80]}..."):
                        st.markdown(f"**Full Question:** {q}")
                        st.info(
                            "💡 **Tip:** Use STAR method (Situation, Task, Action, Result) "
                            "for behavioral questions. Reference Playwright, Appium, or AI "
                            "project experience for technical ones."
                        )
            else:
                st.info("No interview questions generated.")
    else:
        st.info("👈 Select a job match to generate interview questions.")
