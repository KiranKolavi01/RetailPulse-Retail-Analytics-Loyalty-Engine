"""
customer_loyalty.py — RetailPulse Customer Loyalty Distribution Page
Source: RETAILPULSE_FRONTEND.md Page 3 — Customer Loyalty Distribution.
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
    section_header("Customer Loyalty")
    st.markdown("Loyalty tier distribution across all customers.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_rfm_summary())
        except Exception as e:
            show_api_error(e, context="loyalty data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Detect loyalty tier column ────────────────────────────────────────────
    tier_col = next(
        (c for c in df.columns if "tier" in c.lower() or "loyalty" in c.lower()),
        None,
    )

    total_customers = safe_count(df)

    def tier_count(tier_name: str) -> int:
        if tier_col is None:
            return 0
        return int((df[tier_col].astype(str).str.upper() == tier_name.upper()).sum())

    gold_count   = tier_count("Gold")
    silver_count = tier_count("Silver")
    bronze_count = tier_count("Bronze")

    render_metric_row([
        ("Total Customers",  f"{total_customers:,}", ""),
        ("Gold Tier",        f"{gold_count:,}",      ""),
        ("Silver Tier",      f"{silver_count:,}",    ""),
        ("Bronze Tier",      f"{bronze_count:,}",    ""),
    ])

    st.divider()

    # ── Plotly Pie Chart — Loyalty Tier Distribution ──────────────────────────
    if tier_col:
        try:
            tier_counts = df[tier_col].value_counts().reset_index()
            tier_counts.columns = ["Tier", "Count"]

            fig = px.pie(
                tier_counts,
                names="Tier",
                values="Count",
                title="Loyalty Tier Distribution",
                color_discrete_sequence=["#34ACED", "#F59E0B", "#10B981", "#EF4444"],
            )
            fig.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font_family="Inter",
                title_font_family="Montserrat",
                title_font_color="#111827",
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Chart unavailable — loyalty tier column not found.")
    else:
        st.info("Chart unavailable — loyalty tier column not found in data.")

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("All Customer Records")
    render_table(df)
