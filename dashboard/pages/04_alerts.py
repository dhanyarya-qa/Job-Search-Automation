"""
Alerts Dashboard — View and manage job alerts.
"""

from __future__ import annotations

import httpx
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(page_title="Alerts | ATS", page_icon="🔔", layout="wide")
st.markdown("## 🔔 Alerts Dashboard")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

unread_only = st.toggle("Show unread only", value=False)

if st.button("✅ Mark All Read"):
    try:
        resp = httpx.post(f"{API_URL}/api/v1/alerts/mark-all-read", headers=headers, timeout=10)
        if resp.status_code == 200:
            st.success(f"Marked {resp.json()['marked_read']} alerts as read")
    except Exception as e:
        st.error(str(e))

try:
    resp = httpx.get(
        f"{API_URL}/api/v1/alerts/",
        params={"unread_only": unread_only},
        headers=headers,
        timeout=10,
    )
    if resp.status_code == 200:
        data = resp.json()
        st.markdown(f"**{data['count']} alerts**")
        for alert in data["results"]:
            icon = "🔴" if not alert["is_read"] else "⚪"
            with st.expander(f"{icon} {alert['title']} — {alert['created_at'][:10]}"):
                st.write(alert["message"])
                st.caption(f"Type: {alert['alert_type']}")
except Exception as e:
    st.error(f"Error: {e}")
