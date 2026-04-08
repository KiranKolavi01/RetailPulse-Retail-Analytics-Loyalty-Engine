"""
rejected_records.py — RetailPulse Rejected Records Page
Source: RETAILPULSE_FRONTEND.md Page 8 — Rejected Records.
"""
import streamlit as st
import pandas as pd


REJECTED_TABLES = [
    "stores_rejected",
    "products_rejected",
    "customer_details_rejected",
    "store_sales_header_rejected",
    "store_sales_line_items_rejected",
    "promotion_details_rejected",
    "loyalty_rules_rejected",
]


def render():
    from custom_styles import apply_theme, section_header, show_warning
    from helpers import safe_count, render_table, show_api_error, render_metric_row
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()
    section_header("Rejected Records")
    st.markdown("Inspect records that failed validation during the ETL pipeline.")
    st.divider()

    # ── Dropdown selector ─────────────────────────────────────────────────────
    st.markdown(
        "<p style='color: #111827; font-size: 14px; margin-bottom: 4px;'>Select rejected table:</p>",
        unsafe_allow_html=True,
    )
    selected_table = st.selectbox(
        "Select rejected table:",
        REJECTED_TABLES,
        label_visibility="collapsed",
        key="rejected_table_selector",
    )

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_rejected(selected_table))
        except Exception as e:
            show_api_error(e, context=f"{selected_table} data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Ensure reject_reason is first column ──────────────────────────────────
    reason_col = next(
        (c for c in df.columns if "reason" in c.lower() or "reject" in c.lower()),
        None,
    )
    if reason_col and reason_col in df.columns:
        cols = [reason_col] + [c for c in df.columns if c != reason_col]
        df = df[cols]

    # ── Summary Card ──────────────────────────────────────────────────────────
    total_rejected = safe_count(df)

    render_metric_row([
        ("Total Rejected Records", f"{total_rejected:,}", ""),
    ])

    # ── Warning Banner ────────────────────────────────────────────────────────
    if total_rejected > 0:
        show_warning(
            f"⚠ {total_rejected} records rejected. Check reject_reason for details."
        )

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader(f"Rejected Records — {selected_table}")
    render_table(df)
