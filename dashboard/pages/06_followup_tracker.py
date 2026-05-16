"""
Follow-Up Tracker Page — Track application follow-ups and deadlines.
"""

from __future__ import annotations

import httpx
import pandas as pd
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(
    page_title="Follow-Up Tracker | ATS",
    page_icon="📅",
    layout="wide",
)
st.markdown("## 📅 Follow-Up Tracker")
st.caption("Track your job applications and never miss a follow-up")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# ─── Status Update Panel ──────────────────────────────────────────
tab_list, tab_add = st.tabs(["📋 Applications", "➕ Add Application"])

with tab_list:
    try:
        resp = httpx.get(
            f"{API_URL}/api/v1/applications/",
            headers=headers,
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            apps = data.get("results", [])

            if not apps:
                st.info("No applications tracked yet. Add one in the '➕ Add Application' tab.")
            else:
                STATUS_COLORS = {
                    "pending": "🟡",
                    "applied": "🔵",
                    "screening": "🟣",
                    "interview": "🟠",
                    "offer": "🟢",
                    "rejected": "🔴",
                    "withdrawn": "⚫",
                }

                st.markdown(f"**Total applications: {data['count']}**")
                st.divider()

                STATUS_OPTIONS = [
                    "pending", "applied", "screening",
                    "interview", "offer", "rejected", "withdrawn",
                ]

                for app in apps:
                    icon = STATUS_COLORS.get(app["status"], "⚪")
                    with st.expander(
                        f"{icon} Application `{app['id'][:8]}...` — Status: **{app['status'].upper()}**"
                    ):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"**Job ID:** `{app['job_id']}`")
                            st.write(f"**Current Status:** {app['status']}")
                        with col_b:
                            new_status = st.selectbox(
                                "Update Status",
                                STATUS_OPTIONS,
                                index=STATUS_OPTIONS.index(app["status"]),
                                key=f"status_{app['id']}",
                            )
                            if st.button("💾 Save", key=f"save_{app['id']}"):
                                upd_resp = httpx.patch(
                                    f"{API_URL}/api/v1/applications/{app['id']}/status",
                                    json={"status": new_status},
                                    headers=headers,
                                    timeout=10,
                                )
                                if upd_resp.status_code == 200:
                                    st.success(f"Updated to {new_status}")
                                    st.rerun()
                                else:
                                    st.error("Update failed")
        else:
            st.error(f"API error: {resp.status_code}")
    except Exception as e:
        st.error(f"Connection error: {e}")

with tab_add:
    st.subheader("Add New Application")
    job_id_input = st.text_input(
        "Job ID (UUID from Job Explorer)",
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    )
    notes_input = st.text_area("Notes", placeholder="Interview scheduled for...", height=100)

    if st.button("➕ Track Application", type="primary"):
        if not job_id_input:
            st.error("Job ID is required")
        else:
            try:
                create_resp = httpx.post(
                    f"{API_URL}/api/v1/applications/",
                    json={"job_id": job_id_input, "notes": notes_input},
                    headers=headers,
                    timeout=10,
                )
                if create_resp.status_code == 200:
                    st.success("✅ Application tracked successfully!")
                    st.rerun()
                else:
                    detail = create_resp.json().get("detail", "Unknown error")
                    st.error(f"Error: {detail}")
            except Exception as e:
                st.error(f"Connection error: {e}")

# ─── Stats Overview ───────────────────────────────────────────────
st.divider()
st.subheader("📊 Application Pipeline")

try:
    resp = httpx.get(f"{API_URL}/api/v1/applications/", headers=headers, timeout=10)
    if resp.status_code == 200:
        apps = resp.json().get("results", [])
        if apps:
            status_counts: dict[str, int] = {}
            for app in apps:
                s = app["status"]
                status_counts[s] = status_counts.get(s, 0) + 1

            pipeline_stages = ["pending", "applied", "screening", "interview", "offer"]
            cols = st.columns(len(pipeline_stages))
            for col, stage in zip(cols, pipeline_stages):
                count = status_counts.get(stage, 0)
                col.metric(stage.capitalize(), count)
except Exception:
    pass
