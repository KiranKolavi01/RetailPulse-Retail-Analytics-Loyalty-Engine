"""
signup.py — RetailPulse Sign Up Page
"""
import streamlit as st


def render():
    from custom_styles import apply_theme
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
                        Create your account
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            username = st.text_input("Username", placeholder="Enter username",
                                     key="signup_username", label_visibility="collapsed")
            email = st.text_input("Email", placeholder="Enter email address",
                                  key="signup_email", label_visibility="collapsed")
            password = st.text_input("Password", type="password",
                                     placeholder="Enter password",
                                     key="signup_password", label_visibility="collapsed")
            confirm = st.text_input("Confirm Password", type="password",
                                    placeholder="Confirm password",
                                    key="signup_confirm", label_visibility="collapsed")

            error_slot = st.empty()

            b1, b2 = st.columns(2)
            create = b1.button("Create Account", key="signup_btn", use_container_width=True)
            go_signin = b2.button("Sign In", key="goto_signin_btn", use_container_width=True)

            if create:
                if not username or not email or not password or not confirm:
                    error_slot.error("All fields are required.")
                elif password != confirm:
                    error_slot.error("Passwords do not match.")
                elif "@" not in email or "." not in email:
                    error_slot.error("Please enter a valid email address.")
                else:
                    client = RetailPulseClient(BASE_URL)
                    try:
                        client.signup(username, email, password)
                        st.session_state["signup_success"] = True
                        st.session_state["auth_page"] = "signin"
                        st.rerun()
                    except Exception as e:
                        err = str(e).lower()
                        if "username" in err and ("taken" in err or "exists" in err or "duplicate" in err):
                            error_slot.error("Username already taken.")
                        elif "email" in err and ("taken" in err or "exists" in err or "duplicate" in err):
                            error_slot.error("Email already registered.")
                        else:
                            show_api_error(e, context="sign up")

            if go_signin:
                st.session_state["auth_page"] = "signin"
                st.rerun()
