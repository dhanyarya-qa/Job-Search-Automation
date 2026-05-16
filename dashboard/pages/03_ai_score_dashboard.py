"""
AI Score Dashboard — Visualize AI match scores and distributions.
"""

from __future__ import annotations

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(page_title="AI Score Dashboard | ATS", page_icon="🤖", layout="wide")
st.markdown("## 🤖 AI Score Dashboard")

if "access_token" not in st.session_state:
    st.warning("Please login first.")
    st.stop()

token = st.session_state["access_token"]
headers = {"Authorization": f"Bearer {token}"}

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Score Distribution")
    try:
        resp = httpx.get(f"{API_URL}/api/v1/ai-analysis/score-distribution", headers=headers, timeout=10)
        if resp.status_code == 200:
            dist = resp.json()["distribution"]
            fig = px.bar(
                x=list(dist.keys()),
                y=list(dist.values()),
                labels={"x": "Score Range", "y": "Job Count"},
                color=list(dist.values()),
                color_continuous_scale="Viridis",
            )
            fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading distribution: {e}")

with col2:
    st.subheader("🚀 Top Matches")
    min_score = st.slider("Minimum Score", 0, 100, 75)
    try:
        resp = httpx.get(
            f"{API_URL}/api/v1/ai-analysis/top-matches",
            params={"min_score": min_score, "limit": 10},
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            matches = resp.json()["results"]
            if matches:
                df = pd.DataFrame(matches)
                st.dataframe(df[["match_score", "job_category", "prediction_market"]], use_container_width=True)
            else:
                st.info("No matches above threshold.")
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()
st.subheader("📈 Prediction Market Summary")
gauges = [
    ("Bullish Jobs", 72, "#00b09b"),
    ("Neutral Jobs", 18, "#2196F3"),
    ("Bearish Jobs", 10, "#f44336"),
]
cols = st.columns(3)
for col, (label, val, color) in zip(cols, gauges):
    with col:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            title={"text": label},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": color}},
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)
