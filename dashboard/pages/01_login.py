"""
Login Page — OTP-based authentication.
"""

from __future__ import annotations

import httpx
import streamlit as st

from app.config import settings

API_URL = settings.fastapi_base_url

st.set_page_config(page_title="Login | ATS", page_icon="🔐")

st.markdown("## 🔐 Login to ATS Command Center")
st.markdown("---")

tab1, tab2 = st.tabs(["Request OTP", "Verify OTP"])

with tab1:
    username = st.text_input("Username (your full name)", placeholder="Dhany Arya Pratama")
    if st.button("🚀 Send OTP", type="primary"):
        if not username:
            st.error("Please enter your username.")
        else:
            try:
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
                else:
                    st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error: {e}")

with tab2:
    user = st.text_input("Username", value=st.session_state.get("login_username", ""))
    otp_code = st.text_input("OTP Code", max_chars=6, placeholder="123456")
    if st.button("✅ Verify OTP", type="primary"):
        if not user or not otp_code:
            st.error("Please fill in both fields.")
        else:
            try:
                resp = httpx.post(
                    f"{API_URL}/api/v1/auth/verify-otp",
                    json={"username": user, "otp_code": otp_code},
                    timeout=10,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["refresh_token"] = data["refresh_token"]
                    st.success("🎉 Login successful! Navigate to Job Explorer.")
                    st.rerun()
                else:
                    st.error(f"Error: {resp.json().get('detail', 'Invalid OTP')}")
            except Exception as e:
                st.error(f"Connection error: {e}")
