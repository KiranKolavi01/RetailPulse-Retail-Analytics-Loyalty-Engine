"""
rfm_segmentation.py — RetailPulse RFM Segmentation View Page
Source: RETAILPULSE_FRONTEND.md Page 6 — RFM Segmentation View.
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
    section_header("RFM Segmentation")
    st.markdown("Recency, Frequency, and Monetary segmentation of all customers.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            df = pd.DataFrame(client.get_rfm_summary())
        except Exception as e:
            show_api_error(e, context="RFM data")
            return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Detect columns ────────────────────────────────────────────────────────
    segment_col  = next((c for c in df.columns if "segment" in c.lower()), None)
    monetary_col = next((c for c in df.columns if "monetary" in c.lower() or "spend" in c.lower()), None)
    freq_col     = next((c for c in df.columns if "frequency" in c.lower() or "freq" in c.lower()), None)

    total_customers = safe_count(df)

    hs_count = 0
    ar_count = 0
    if segment_col:
        seg_upper = df[segment_col].astype(str).str.upper()
        hs_count = int((seg_upper == "HS").sum())
        ar_count = int((seg_upper == "AR").sum())

    avg_monetary = safe_mean(df, monetary_col) if monetary_col else 0.0

    render_metric_row([
        ("Total Customers",    f"{total_customers:,}", ""),
        ("High Spenders (HS)", f"{hs_count:,}",        ""),
        ("At Risk (AR)",       f"{ar_count:,}",        ""),
        ("Avg Monetary Value", f"${avg_monetary:,.1f}", ""),
    ])

    st.divider()

    # ── Plotly Scatter — Frequency vs Monetary, colored by segment ────────────
    if freq_col and monetary_col:
        try:
            scatter_df = df.copy()
            scatter_df[freq_col]     = pd.to_numeric(scatter_df[freq_col],     errors="coerce").fillna(0)
            scatter_df[monetary_col] = pd.to_numeric(scatter_df[monetary_col], errors="coerce").fillna(0)

            color_map = {"HS": "#34ACED", "AR": "#EF4444"}

            if segment_col:
                scatter_df["_seg_upper"] = scatter_df[segment_col].astype(str).str.upper()
                fig = px.scatter(
                    scatter_df,
                    x=freq_col,
                    y=monetary_col,
                    color="_seg_upper",
                    color_discrete_map=color_map,
                    title="RFM Segmentation: Frequency vs Monetary",
                    labels={
                        freq_col:     "Frequency",
                        monetary_col: "Monetary Value ($)",
                        "_seg_upper": "Segment",
                    },
                )
            else:
                fig = px.scatter(
                    scatter_df,
                    x=freq_col,
                    y=monetary_col,
                    title="RFM Segmentation: Frequency vs Monetary",
                    labels={freq_col: "Frequency", monetary_col: "Monetary Value ($)"},
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
            st.info("Chart unavailable — frequency or monetary column not found.")
    else:
        st.info("Chart unavailable — frequency or monetary column not found in data.")

    # ── Reference Card ────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style='
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 20px 24px;
            margin: 16px 0;
        '>
            <p style='font-weight: 700; color: #111827; margin-bottom: 8px; font-family: Montserrat, sans-serif;'>Segment Definitions</p>
            <p style='color: #111827; font-size: 14px; margin-bottom: 6px;'>
                <span style='color: #34ACED; font-weight: 700;'>HS — High Spenders:</span>
                Customers in the top 20% of monetary value. HS classification takes priority over AR.
            </p>
            <p style='color: #111827; font-size: 14px; margin: 0;'>
                <span style='color: #EF4444; font-weight: 700;'>AR — At Risk:</span>
                Customers with no purchase in 30+ days who are not already classified as HS.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("Full RFM Data")
    render_table(df)
