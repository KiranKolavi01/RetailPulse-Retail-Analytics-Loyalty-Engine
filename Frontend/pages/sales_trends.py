"""
sales_trends.py — RetailPulse Sales Trends Page
Source: RETAILPULSE_FRONTEND.md Page 2 — Sales Trends.
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
    section_header("Sales Trends")
    st.markdown("Sales performance over time across all stores.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_sales_header())
        except Exception as e:
            show_api_error(e, context="sales data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Summary Cards ─────────────────────────────────────────────────────────
    total_transactions = safe_count(df)

    revenue_col = next((c for c in df.columns if "revenue" in c.lower() or "total" in c.lower() or "amount" in c.lower()), None)
    total_revenue = safe_sum(df, revenue_col) if revenue_col else 0.0
    avg_transaction = safe_mean(df, revenue_col) if revenue_col else 0.0

    store_col = next((c for c in df.columns if "store" in c.lower()), None)
    total_stores = len(df[store_col].dropna().unique()) if store_col else 0

    render_metric_row([
        ("Total Transactions", f"{total_transactions:,}", ""),
        ("Total Revenue", f"${total_revenue:,.1f}", ""),
        ("Avg Transaction Value", f"${avg_transaction:,.1f}", ""),
        ("Total Stores Active", str(total_stores), ""),
    ])

    st.divider()

    # ── Plotly Line Chart — Sales Over Time ───────────────────────────────────
    date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)
    if date_col and revenue_col:
        try:
            chart_df = df[[date_col, revenue_col]].copy()
            chart_df[date_col] = pd.to_datetime(chart_df[date_col], errors="coerce")
            chart_df[revenue_col] = pd.to_numeric(chart_df[revenue_col], errors="coerce").fillna(0)
            chart_df = chart_df.dropna(subset=[date_col]).sort_values(date_col)

            fig = px.line(
                chart_df,
                x=date_col,
                y=revenue_col,
                title="Sales Revenue Over Time",
                labels={date_col: "Date", revenue_col: "Revenue"},
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
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Chart unavailable — date or revenue column not found.")
    else:
        st.info("Chart unavailable — date or revenue column not found in data.")

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("All Sales Records")
    render_table(df)
