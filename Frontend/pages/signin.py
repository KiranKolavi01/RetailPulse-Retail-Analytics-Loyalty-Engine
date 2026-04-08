"""
signin.py — RetailPulse Sign In Page
"""
import streamlit as st


def render():
    from custom_styles import apply_theme, show_success
    from helpers import show_api_error
    from client import RetailPulseClient
    from config import BASE_URL

    apply_theme()

    st.markdown(
        """
        <style>
        .main > div { padding-top: 0rem !important; }
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
        [data-testid="stAppViewContainer"] > section.main { padding-top: 0 !important; }
        div[data-testid="stMarkdownContainer"] {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        div[data-testid="element-container"]:has(div[data-testid="stMarkdownContainer"]) {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("signup_success"):
        show_success("Account created successfully. Please sign in.")
        st.session_state["signup_success"] = False

    _, col, _ = st.columns([1, 1.2, 1])

    with col:
        with st.container(border=True):
            st.markdown(
                """
                <div style='text-align:center; margin-bottom:12px;'>
                    <h2 style='font-family:Montserrat,sans-serif; font-weight:600;
                        color:#111827; letter-spacing:0.02em; margin:0 0 2px 0;'>
                        RETAILPULSE
                    </h2>
                    <p style='color:#6B7280; font-size:13px; margin:0;'>
                        Sign in to your account
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            username = st.text_input("Username", placeholder="Enter username",
                                     key="signin_username", label_visibility="collapsed")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter password",
                                     key="signin_password", label_visibility="collapsed")

            error_slot = st.empty()

            b1, b2 = st.columns(2)
            sign_in = b1.button("Sign In", key="signin_btn", use_container_width=True)
            sign_up = b2.button("Sign Up", key="goto_signup_btn", use_container_width=True)

            if sign_in:
                if not username or not password:
                    error_slot.error("Username and password are required.")
                else:
                    client = RetailPulseClient(BASE_URL)
                    try:
                        client.signin(username, password)
                        st.session_state["username"] = username
                        st.session_state["current_page"] = "Run Pipeline"
                        st.query_params["page"] = "Run Pipeline"
                        st.rerun()
                    except Exception as e:
                        err = str(e).lower()
                        if "401" in err or "403" in err or "invalid" in err or "credential" in err or "password" in err:
                            error_slot.error("Invalid username or password.")
                        else:
                            show_api_error(e, context="sign in")

            if sign_up:
                st.session_state["auth_page"] = "signup"
                st.rerun()
