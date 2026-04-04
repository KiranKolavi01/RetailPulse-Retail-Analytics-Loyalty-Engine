"""
at_risk_alerts.py — RetailPulse At-Risk Customer Alerts Page
Source: RETAILPULSE_FRONTEND.md Page 4 — At-Risk Customer Alerts.
"""
import streamlit as st
import pandas as pd


def render():
    from custom_styles import apply_theme, section_header, show_warning
    from helpers import safe_mean, safe_sum, safe_count, render_table, show_api_error, render_metric_row
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()
    section_header("At-Risk Alerts")
    st.markdown("Customers at risk of churn — no purchase in 30+ days.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_rfm_summary())
        except Exception as e:
            show_api_error(e, context="at-risk data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Filter to AR segment ──────────────────────────────────────────────────
    segment_col = next(
        (c for c in df.columns if "segment" in c.lower()),
        None,
    )

    if segment_col:
        ar_df = df[df[segment_col].astype(str).str.upper() == "AR"].copy()
    else:
        # Fallback: filter by recency if segment column not present
        recency_col = next((c for c in df.columns if "recency" in c.lower() or "days" in c.lower()), None)
        if recency_col:
            df[recency_col] = pd.to_numeric(df[recency_col], errors="coerce").fillna(0)
            ar_df = df[df[recency_col] >= 30].copy()
        else:
            ar_df = df.copy()

    at_risk_count = safe_count(ar_df)

    # ── Warning Banner ────────────────────────────────────────────────────────
    show_warning(f"⚠ {at_risk_count} customers at risk of churn. Retention campaigns recommended.")

    # ── Summary Cards ─────────────────────────────────────────────────────────
    recency_col = next(
        (c for c in ar_df.columns if "recency" in c.lower() or "days" in c.lower()),
        None,
    )
    monetary_col = next(
        (c for c in ar_df.columns if "monetary" in c.lower() or "revenue" in c.lower() or "spend" in c.lower()),
        None,
    )

    avg_days = safe_mean(ar_df, recency_col) if recency_col else 0.0
    total_revenue_at_risk = safe_sum(ar_df, monetary_col) if monetary_col else 0.0

    render_metric_row([
        ("Total At-Risk Customers", f"{at_risk_count:,}", ""),
        ("Avg Days Since Purchase",  f"{avg_days:.1f}",   " days"),
        ("Total Revenue at Risk",    f"${total_revenue_at_risk:,.1f}", ""),
    ])

    st.divider()

    # ── Color-coded table ─────────────────────────────────────────────────────
    st.subheader("At-Risk Customers")

    if ar_df is None or ar_df.empty:
        st.info("No at-risk customers found.")
        return

    # Apply row color coding via pandas Styler
    def color_row(row):
        if recency_col and recency_col in row.index:
            days = pd.to_numeric(row[recency_col], errors="coerce")
            if pd.isna(days):
                return [""] * len(row)
            if days > 60:
                # Danger — darker red
                return [f"background-color: #FEE2E2; color: #991B1B"] * len(row)
            elif days >= 30:
                # Warning — amber
                return [f"background-color: #FEF3C7; color: #92400E"] * len(row)
        return [""] * len(row)

    try:
        styled = ar_df.style.apply(color_row, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)
    except Exception:
        render_table(ar_df)
