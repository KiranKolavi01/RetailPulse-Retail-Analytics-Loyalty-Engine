"""
helpers.py — RetailPulse Bug Prevention Layer
Every function here exists to prevent a known bug from the previous project.
Source: FRONTEND_DESIGN_SYSTEM.md Section 16 + task spec.
"""
import streamlit as st
import pandas as pd
import requests


def safe_numeric(df: pd.DataFrame, col: str) -> pd.Series:
    """
    Convert column to numeric, never crash, never return NaN.
    Always returns float, 0.0 if conversion fails.
    """
    return pd.to_numeric(df[col], errors="coerce").fillna(0)


def safe_mean(df: pd.DataFrame, col: str) -> float:
    """
    Compute mean safely, return 0.0 if NaN.
    Rounded to 1 decimal.
    """
    result = pd.to_numeric(df[col], errors="coerce").mean()
    return round(result, 1) if not pd.isna(result) else 0.0


def safe_sum(df: pd.DataFrame, col: str) -> float:
    """
    Compute sum safely, return 0.0 if NaN.
    Rounded to 1 decimal.
    """
    result = pd.to_numeric(df[col], errors="coerce").sum()
    return round(result, 1) if not pd.isna(result) else 0.0


def safe_count(df: pd.DataFrame, col=None) -> int:
    """
    Return row count, 0 if empty.
    """
    if df is None or df.empty:
        return 0
    return len(df)


def render_table(df: pd.DataFrame, color_rules=None):
    """
    Standard interactive table — never crashes on empty df.
    color_rules = dict of {col: {value: css_color}} (reserved for future use).
    Always uses st.dataframe with use_container_width=True.
    """
    if df is None or df.empty:
        st.info("No data available. Run the pipeline first.")
        return
    st.dataframe(df, use_container_width=True, hide_index=True)


def show_api_error(e: Exception, context: str = "data"):
    """
    Never shows raw traceback.
    Detects network vs API error and shows a friendly message.
    """
    from custom_styles import show_error
    error_str = str(e).lower()
    if "connection" in error_str or "refused" in error_str:
        show_error(
            f"Cannot connect to backend. "
            f"Is the FastAPI server running at the configured URL?"
        )
    elif "404" in error_str:
        show_error(f"No {context} found. Run the pipeline first.")
    elif "401" in error_str or "403" in error_str:
        show_error("Session expired. Please sign in again.")
    else:
        show_error(f"Error loading {context}: {str(e)}")


def render_metric_row(metrics: list):
    """
    Render a row of metric cards.
    metrics = list of (title, value, unit) tuples.
    Always renders in columns, handles 1–4 metrics.
    """
    from custom_styles import metric_card
    cols = st.columns(len(metrics))
    for i, (title, value, unit) in enumerate(metrics):
        with cols[i]:
            metric_card(title, value, unit)


def check_backend_connection(base_url: str) -> bool:
    """
    Call on startup, return True/False.
    Show red banner if unreachable.
    """
    from custom_styles import show_error
    try:
        requests.get(f"{base_url}/", timeout=3)
        return True
    except Exception:
        show_error(
            f"Backend not reachable at {base_url}. "
            f"Please start the FastAPI server."
        )
        return False
