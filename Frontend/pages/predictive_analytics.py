"""
predictive_analytics.py — RetailPulse Predictive Analytics Page
Source: RETAILPULSE_FRONTEND.md Page 7 — Predictive Analytics.
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def render():
    from custom_styles import apply_theme, section_header
    from helpers import safe_mean, safe_sum, safe_count, render_table, show_api_error, render_metric_row
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()
    section_header("Predictive Analytics")
    st.markdown("Machine learning predictions for customer spend, restock needs, and promotion sensitivity.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_customer_predictions())
        except Exception as e:
            show_api_error(e, context="predictions data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Detect columns ────────────────────────────────────────────────────────
    spend_col  = next((c for c in df.columns if "spend" in c.lower() or "predicted" in c.lower()), None)
    restock_col = next((c for c in df.columns if "restock" in c.lower()), None)
    promo_col  = next((c for c in df.columns if "promo" in c.lower() or "sensitivity" in c.lower()), None)

    total_customers = safe_count(df)
    avg_spend       = safe_mean(df, spend_col) if spend_col else 0.0

    restock_count = 0
    if restock_col:
        restock_series = df[restock_col].astype(str).str.upper()
        restock_count = int(restock_series.isin(["TRUE", "1", "YES"]).sum())

    high_promo_count = 0
    if promo_col:
        high_promo_count = int((df[promo_col].astype(str).str.upper() == "HIGH").sum())

    render_metric_row([
        ("Customers with Predictions", f"{total_customers:,}",  ""),
        ("Avg Predicted Spend",        f"${avg_spend:,.1f}",    ""),
        ("Restock Flags",              f"{restock_count:,}",    ""),
        ("High Promo Sensitivity",     f"{high_promo_count:,}", ""),
    ])

    st.divider()

    # ── Plotly Histogram — Predicted Spend Distribution ───────────────────────
    if spend_col:
        try:
            hist_df = df.copy()
            hist_df[spend_col] = pd.to_numeric(hist_df[spend_col], errors="coerce").fillna(0)

            fig = px.histogram(
                hist_df,
                x=spend_col,
                nbins=30,
                title="Predicted Spend Distribution",
                labels={spend_col: "Predicted Next Month Spend ($)"},
                color_discrete_sequence=["#34ACED"],
            )
            fig.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font_family="Inter",
                title_font_family="Montserrat",
                title_font_color="#111827",
                xaxis=dict(gridcolor="#E5E7EB"),
                yaxis=dict(gridcolor="#E5E7EB"),
                bargap=0.05,
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Chart unavailable — predicted spend column not found.")
    else:
        st.info("Chart unavailable — predicted spend column not found in data.")

    st.divider()

    # ── Color-coded Table ─────────────────────────────────────────────────────
    st.subheader("Customer Predictions")

    if df is None or df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    def color_row(row):
        styles = [""] * len(row)
        cols = list(row.index)

        # Color promotion_sensitivity
        if promo_col and promo_col in cols:
            val = str(row[promo_col]).upper()
            idx = cols.index(promo_col)
            if val == "HIGH":
                styles[idx] = "background-color: #FEE2E2; color: #991B1B"
            elif val == "MEDIUM":
                styles[idx] = "background-color: #FEF3C7; color: #92400E"
            elif val == "LOW":
                styles[idx] = "background-color: #D1FAE5; color: #065F46"

        # Color restock_flag
        if restock_col and restock_col in cols:
            val = str(row[restock_col]).upper()
            idx = cols.index(restock_col)
            if val in ("TRUE", "1", "YES"):
                styles[idx] = "background-color: #FEE2E2; color: #991B1B"
            else:
                styles[idx] = "background-color: #D1FAE5; color: #065F46"

        return styles

    try:
        styled = df.style.apply(color_row, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)
    except Exception:
        render_table(df)
