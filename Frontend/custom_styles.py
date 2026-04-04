"""
custom_styles.py — RetailPulse Design System
Reproduced verbatim from FRONTEND_DESIGN_SYSTEM.md (all 17 sections).
"""
import streamlit as st

# ── SECTION 2 — COLORS ────────────────────────────────────────────────────────
COLORS = {
    # Background & Surface
    "page_background":        "#F8F9FB",
    "sidebar_background":     "#FFFFFF",
    "card_surface":           "#FFFFFF",
    "table_background":       "#FFFFFF",
    "nav_hover_bg":           "#F8F9FB",
    "active_nav_bg":          "#F0F9FF",

    # Text
    "primary_text":           "#111827",
    "secondary_text":         "#6B7280",
    "sidebar_inactive_nav":   "#4B5563",
    "sidebar_active_nav":     "#34ACED",
    "brand_name_text":        "#000000",
    "metric_value":           "#000000",
    "sidebar_footer_text":    "#999999",

    # Accent
    "primary_accent":         "#34ACED",
    "accent_hover":           "#34ACED",
    "active_nav_border":      "#BAE6FD",

    # Borders & Dividers
    "card_border":            "#E5E7EB",
    "sidebar_border":         "#E5E7EB",
    "divider":                "#E5E7EB",
    "table_border":           "#E5E7EB",
    "grid_line":              "#E5E7EB",
    "badge_border":           "#E5E7EB",

    # Status — Success
    "success_bg":             "#D1FAE5",
    "success_text":           "#065F46",
    "success_border":         "#10B981",
    "dot_success":            "#10B981",

    # Status — Warning
    "warning_bg":             "#FEF3C7",
    "warning_text":           "#92400E",
    "warning_border":         "#F59E0B",
    "dot_warning":            "#F59E0B",

    # Status — Danger
    "danger_bg":              "#FEE2E2",
    "danger_text":            "#991B1B",
    "danger_border":          "#EF4444",
    "dot_error":              "#EF4444",

    # Button
    "button_bg":              "#000000",
    "button_text":            "#FFFFFF",
    "button_hover_bg":        "#34ACED",
}

# ── SECTION 1 — FONTS ─────────────────────────────────────────────────────────
FONTS = {
    "import_inter":      "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap",
    "import_michroma":   "https://fonts.googleapis.com/css2?family=Michroma&display=swap",
    "import_montserrat": "https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap",
    "body":              "Inter",
    "heading":           "Montserrat",
    "brand":             "Michroma",
    "metric_value_size": "2.2rem",
    "metric_label_size": "0.65rem",
    "nav_item_size":     "0.95rem",
    "button_size":       "13px",
    "tech_label_size":   "14px",
    "sidebar_footer_size": "11px",
}

# ── SECTION 3 — SPACING ───────────────────────────────────────────────────────
SPACING = {
    "card_padding":        "24px",
    "card_border_radius":  "6px",
    "nav_item_padding":    "8px 12px",
    "nav_item_margin_bottom": "2px",
    "nav_item_border_radius": "4px",
    "nav_item_gap":        "0.2rem",
    "divider_margin":      "2rem 0",
    "button_padding":      "0.75rem 1.5rem",
    "button_border_radius": "4px",
    "badge_padding":       "4px 10px",
    "badge_border_radius": "100px",
    "status_dot_size":     "6px",
    "viz_card_padding":    "24px",
    "viz_card_margin_bottom": "24px",
    "viz_card_border_radius": "6px",
    "grid_size":           "40px 40px",
    "sidebar_padding_top": "1rem",
}


def apply_theme():
    """
    Inject global CSS from FRONTEND_DESIGN_SYSTEM.md Section 17 verbatim.
    Call as the very first line inside every render() function.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Michroma&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap');

        /* Main body background and technical grid */
        .stApp { 
            background-color: #F8F9FB; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            color: #111827;
            background-image: 
                linear-gradient(#E5E7EB 1px, transparent 1px),
                linear-gradient(90deg, #E5E7EB 1px, transparent 1px);
            background-size: 40px 40px;
            background-position: center;
        }

        .stApp::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle at 100% 0%, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 251, 0.8) 100%);
            z-index: -1;
        }

        /* Headers */
        h1, h2, h3 { 
            font-family: 'Montserrat', sans-serif !important;
            color: #111827 !important; 
            font-weight: 600 !important; 
            letter-spacing: 0.02em !important; 
            line-height: 1.2 !important;
            text-transform: none !important;
        }

        /* Branding Font */
        .brand-font {
            font-family: 'Michroma', sans-serif !important;
            text-transform: uppercase !important;
            letter-spacing: -0.02em !important;
            color: #000000 !important;
            font-size: 20px !important;
            margin-bottom: 0 !important;
        }

        /* Technical Status Labels */
        .tech-label {
            font-size: 14px !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.15em !important;
            color: #6B7280 !important;
            margin-bottom: 4px !important;
        }

        /* Sidebar */
        [data-testid="stSidebar"] { 
            background-color: #FFFFFF !important; 
            border-right: 1px solid #E5E7EB !important; 
            padding-top: 1rem;
        }
        [data-testid="stSidebarNav"] { display: none !important; }

        /* Metrics */
        [data-testid="stMetricValue"] { 
            color: #000000 !important; 
            font-weight: 800; 
            font-size: 2.2rem !important;
            letter-spacing: -0.03em;
        }
        [data-testid="stMetricLabel"] { 
            color: #6B7280 !important; 
            font-weight: 800; 
            font-size: 0.65rem; 
            text-transform: uppercase; 
            letter-spacing: 0.12em; 
        }
        [data-testid="stMetric"] { 
            background-color: #FFFFFF; 
            padding: 24px !important; 
            border-radius: 6px; 
            border: 1px solid #E5E7EB;
            box-shadow: none;
            transition: border-color 0.2s;
        }
        [data-testid="stMetric"]:hover { border-color: #34ACED; }

        /* Navigation Radio */
        div[data-testid="stRadio"] { padding: 0 !important; }
        div[data-testid="stRadio"] [role="radiogroup"] { gap: 0.2rem !important; }
        div[data-testid="stRadio"] label {
            padding: 8px 12px !important;
            margin-bottom: 2px !important;
            cursor: pointer !important;
            border-radius: 4px !important;
            border: 1px solid transparent !important;
            background-color: transparent !important;
        }
        div[data-testid="stRadio"] label:hover {
            background-color: #F8F9FB !important;
        }
        div[role="radiogroup"] > label > div:first-child,
        div[data-testid="stRadio"] label div[data-baseweb="radio"],
        .stRadio [role="radio"] > div:first-child,
        .stRadio div[role="radiogroup"] label > div:first-child {
            display: none !important;
            opacity: 0 !important;
            width: 0px !important;
            height: 0px !important;
            overflow: hidden !important;
        }
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p {
            color: #4B5563 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            letter-spacing: -0.01em !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] {
            background-color: #F0F9FF !important;
            border: 1px solid #BAE6FD !important;
        }
        div[data-testid="stRadio"] label[data-checked="true"] div[data-testid="stMarkdownContainer"] p {
            color: #34ACED !important;
            font-weight: 800 !important;
        }

        /* Dividers */
        hr { border-bottom: 1px solid #E5E7EB !important; opacity: 1; margin: 2rem 0 !important; }

        /* DataFrames */
        [data-testid="stDataFrame"] { 
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB; 
            border-radius: 4px; 
            padding: 0;
        }

        /* Buttons */
        .stButton > button, .stDownloadButton > button, div[data-testid="stDownloadButton"] > button {
            background-color: #000000 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px !important; 
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0.75rem 1.5rem !important;
            text-transform: none !important;
            letter-spacing: -0.01em !important;
            transition: all 0.2s ease !important;
        }
        .stButton > button *, .stDownloadButton > button *, div[data-testid="stDownloadButton"] > button * {
            color: #FFFFFF !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover, div[data-testid="stDownloadButton"] > button:hover {
            background-color: #34ACED !important;
            transform: translateY(-1px);
        }
        .stButton > button:active, .stDownloadButton > button:active, div[data-testid="stDownloadButton"] > button:active {
            transform: translateY(0);
        }

        /* Status Badges */
        .status-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 10px;
            border-radius: 100px;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            background-color: #F3F4F6;
            border: 1px solid #E5E7EB;
            color: #4B5563;
        }
        .status-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            margin-right: 6px;
        }
        .dot-success { background-color: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.4); }
        .dot-error { background-color: #EF4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }
        .dot-warning { background-color: #F59E0B; box-shadow: 0 0 8px rgba(245, 158, 11, 0.4); }

        /* Visualization Cards */
        .viz-card {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 6px;
            padding: 24px;
            margin-bottom: 24px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value, unit: str = ""):
    """
    Render a single metric using Streamlit native st.metric().
    If unit is provided and value doesn't already end with it, append it.
    """
    val_str = str(value)
    if unit and not val_str.endswith(unit.strip()):
        display_value = f"{val_str}{unit}"
    else:
        display_value = val_str
    st.metric(label=title, value=display_value)


def section_header(title: str):
    """
    Render a page/section title.
    Section 5 — FRONTEND_DESIGN_SYSTEM.md.
    Uses st.title() — Montserrat 600 #111827 via global CSS.
    """
    st.title(title)


def show_error(message: str):
    """
    Section 10 — Error Banner (page-level).
    Uses Streamlit native st.error().
    """
    st.error(f"⚠️ {message}")


def show_success(message: str):
    """
    Section 10 — Success Banner.
    Custom HTML to match exact design spec colors.
    """
    st.markdown(
        f"""
        <div style='padding: 10px; background-color: #D1FAE5; border: 2px solid #10B981; border-radius: 5px; margin-bottom: 15px;'>
            <p style='color: #065F46; font-weight: bold; margin: 0; font-size: 14px;'>
                ✓ {message}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_warning(message: str):
    """
    Section 10 — Warning Banner.
    Custom HTML to match exact design spec colors.
    """
    st.markdown(
        f"""
        <div style='padding: 14px 18px; background-color: #FEF3C7; border: 1px solid #F59E0B; border-radius: 6px; margin-bottom: 8px;'>
            <p style='color: #92400E; font-size: 14px; font-weight: 600; margin: 0;'>
                {message}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
