"""
app.py — RetailPulse Main Application Entry Point
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="RetailPulse",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 1. SESSION STATE INITIALIZATION ──────────────────────────────────────────
if "username" not in st.session_state:
    st.session_state["username"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Run Pipeline"
if "auth_page" not in st.session_state:
    st.session_state["auth_page"] = "signin"

# ── 2. QUERY PARAMS — PAGE REFRESH FIX ───────────────────────────────────────
params = st.query_params
if "page" in params:
    st.session_state["current_page"] = params["page"]


def navigate_to(page_name: str):
    st.session_state["current_page"] = page_name
    st.query_params["page"] = page_name


# ── 3. AUTH GUARD ─────────────────────────────────────────────────────────────
if st.session_state["username"] is None:
    if st.session_state["auth_page"] == "signin":
        from pages.signin import render
        render()
    else:
        from pages.signup import render
        render()
    st.stop()

# ── 4. APPLY THEME ────────────────────────────────────────────────────────────
from custom_styles import apply_theme
apply_theme()

# ── 5. BACKEND CONNECTION CHECK ───────────────────────────────────────────────
from helpers import check_backend_connection
from config import BASE_URL, PAGE_NAMES
check_backend_connection(BASE_URL)

# ── 6. SIDEBAR ────────────────────────────────────────────────────────────────
def on_nav_change():
    navigate_to(st.session_state["nav_radio"])

with st.sidebar:
    st.markdown('<p class="tech-label">Platform</p>', unsafe_allow_html=True)
    st.markdown('<p class="brand-font">RetailPulse</p>', unsafe_allow_html=True)
    st.markdown('<p class="tech-label" style="margin-top:-5px;">Analytics Dashboard</p>', unsafe_allow_html=True)
    st.divider()

    current_page = st.session_state.get("current_page", "Run Pipeline")
    if current_page not in PAGE_NAMES:
        current_page = PAGE_NAMES[0]
    if "nav_radio" not in st.session_state or st.session_state["nav_radio"] != current_page:
        st.session_state["nav_radio"] = current_page

    st.radio(
        "Navigation",
        PAGE_NAMES,
        key="nav_radio",
        on_change=on_nav_change,
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown(
        f"<div style='font-size:11px;color:#999;letter-spacing:0.05em;'>"
        f"<p><strong>API ENDPOINT</strong><br/>{BASE_URL}</p>"
        f"<p>Signed in as <strong>{st.session_state.get('username','')}</strong></p></div>",
        unsafe_allow_html=True,
    )

    if st.button("Sign Out", key="sign_out_btn"):
        st.session_state["username"] = None
        st.session_state["current_page"] = "Run Pipeline"
        st.session_state["auth_page"] = "signin"
        st.query_params.clear()
        st.rerun()

# ── 7. PAGE ROUTING ───────────────────────────────────────────────────────────
from pages import (
    run_pipeline, sales_trends, customer_loyalty, at_risk_alerts,
    top_products, rfm_segmentation, predictive_analytics,
    rejected_records, visualizations,
)

page_map = {
    "Run Pipeline":         run_pipeline.render,
    "Sales Trends":         sales_trends.render,
    "Customer Loyalty":     customer_loyalty.render,
    "At-Risk Alerts":       at_risk_alerts.render,
    "Top Products":         top_products.render,
    "RFM Segmentation":     rfm_segmentation.render,
    "Predictive Analytics": predictive_analytics.render,
    "Rejected Records":     rejected_records.render,
    "Visualizations":       visualizations.render,
}

current = st.session_state.get("current_page", "Run Pipeline")
page_map.get(current, run_pipeline.render)()
