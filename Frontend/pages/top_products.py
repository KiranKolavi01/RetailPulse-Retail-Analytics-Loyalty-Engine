"""
top_products.py — RetailPulse Top Products Analysis Page
Source: RETAILPULSE_FRONTEND.md Page 5 — Top Products Analysis.
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
    section_header("Top Products")
    st.markdown("Product performance ranked by revenue and quantity sold.")
    st.divider()

    client = RetailPulseClient(BASE_URL)

    with st.spinner("Loading data..."):
        try:
            line_items_data = client.get_sales_line_items()
            products_data   = client.get_products()
        except Exception as e:
            show_api_error(e, context="products data")
            return

    line_df    = pd.DataFrame(line_items_data)
    product_df = pd.DataFrame(products_data)

    # Merge if both have data and share a product key
    if not line_df.empty and not product_df.empty:
        prod_key = next(
            (c for c in line_df.columns if "product" in c.lower() and "id" in c.lower()),
            None,
        )
        prod_key_p = next(
            (c for c in product_df.columns if "product" in c.lower() and "id" in c.lower()),
            None,
        )
        if prod_key and prod_key_p:
            try:
                df = pd.merge(line_df, product_df, left_on=prod_key, right_on=prod_key_p, how="left")
            except Exception:
                df = line_df
        else:
            df = line_df
    elif not line_df.empty:
        df = line_df
    elif not product_df.empty:
        df = product_df
    else:
        st.info("No data available. Run the pipeline first.")
        return

    if df.empty:
        st.info("No data available. Run the pipeline first.")
        return

    # ── Detect columns ────────────────────────────────────────────────────────
    revenue_col = next(
        (c for c in df.columns if "revenue" in c.lower() or "total" in c.lower() or "amount" in c.lower()),
        None,
    )
    qty_col = next(
        (c for c in df.columns if "qty" in c.lower() or "quantity" in c.lower()),
        None,
    )
    price_col = next(
        (c for c in df.columns if "price" in c.lower() or "unit" in c.lower()),
        None,
    )
    name_col = next(
        (c for c in df.columns if "name" in c.lower() or "product_name" in c.lower()),
        None,
    )

    total_products = safe_count(product_df) if not product_df.empty else safe_count(df)
    avg_price      = safe_mean(df, price_col) if price_col else 0.0

    # Top product by revenue
    top_by_revenue = ""
    if revenue_col and name_col:
        try:
            rev_series = pd.to_numeric(df[revenue_col], errors="coerce")
            idx = rev_series.idxmax()
            top_by_revenue = str(df.loc[idx, name_col]) if not pd.isna(idx) else ""
        except Exception:
            top_by_revenue = ""

    # Top product by quantity
    top_by_qty = ""
    if qty_col and name_col:
        try:
            qty_series = pd.to_numeric(df[qty_col], errors="coerce")
            idx = qty_series.idxmax()
            top_by_qty = str(df.loc[idx, name_col]) if not pd.isna(idx) else ""
        except Exception:
            top_by_qty = ""

    render_metric_row([
        ("Total Products",          f"{total_products:,}",    ""),
        ("Top by Revenue",          top_by_revenue or "N/A",  ""),
        ("Top by Quantity",         top_by_qty or "N/A",      ""),
        ("Avg Product Price",       f"${avg_price:,.2f}",     ""),
    ])

    st.divider()

    # ── Plotly Horizontal Bar — Top 10 Products by Revenue ────────────────────
    if revenue_col and name_col:
        try:
            agg_df = (
                df.groupby(name_col)[revenue_col]
                .apply(lambda x: pd.to_numeric(x, errors="coerce").sum())
                .reset_index()
                .rename(columns={revenue_col: "Total Revenue"})
                .sort_values("Total Revenue", ascending=False)
                .head(10)
            )

            fig = px.bar(
                agg_df,
                x="Total Revenue",
                y=name_col,
                orientation="h",
                title="Top 10 Products by Revenue",
                labels={name_col: "Product", "Total Revenue": "Revenue ($)"},
                color_discrete_sequence=["#34ACED"],
            )
            fig.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font_family="Inter",
                title_font_family="Montserrat",
                title_font_color="#111827",
                xaxis=dict(gridcolor="#E5E7EB"),
                yaxis=dict(gridcolor="#E5E7EB", autorange="reversed"),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Chart unavailable — could not aggregate product revenue.")
    else:
        st.info("Chart unavailable — product name or revenue column not found.")

    st.divider()

    # ── Table ─────────────────────────────────────────────────────────────────
    st.subheader("All Products with Sales Data")
    render_table(df)
