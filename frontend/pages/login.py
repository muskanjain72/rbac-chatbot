import streamlit as st
from styles import DESIGN_CSS

st.set_page_config(page_title="fintechAI — Sign in", layout="centered")
st.markdown(
    DESIGN_CSS
    + """
<style>
/* Hide the default multipage sidebar on the login screen */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* Give the login screen more horizontal room */
.block-container {
    max-width: 920px !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Make the auth form feel more deliberate */
.stTextInput label {
    font-size: 16px !important;
    font-weight: 600 !important;
    color: #d7d7d7 !important;
    margin-bottom: 0.35rem !important;
}

.stTextInput input {
    font-size: 18px !important;
    padding: 16px 18px !important;
    min-height: 56px !important;
}

/* Center and slightly narrow the primary action */
div[data-testid="stButton"] > button[kind="primary"] {
    width: min(180px, 100%) !important;
    margin: 10px auto 0 auto !important;
    display: block !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("<div style='height:1vh'></div>", unsafe_allow_html=True)

col_l, col_c, col_r = st.columns([1, 3.2, 1])
with col_c:
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:18px;">
            <span style="font-size:38px; font-weight:400; letter-spacing:-0.65px; color:#ffffff;">
                fintech<span style="color:#00d992;">AI</span>
            </span>
            <p style="color:#8b949e; font-size:15px; margin-top:8px; letter-spacing:2.52px; text-transform:uppercase; font-weight:600;">
                Secure workspace
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='font-size:26px; font-weight:600; letter-spacing:-0.6px; margin-bottom:22px; text-align:center;'>Sign in</p>",
        unsafe_allow_html=True,
    )

    email = st.text_input("Email address", placeholder="you@company.com", key="login_email")
    password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if "login_error" in st.session_state and st.session_state.login_error:
        st.markdown(
            f"<p class='err-text' style='text-align:center;'>⚠ {st.session_state.login_error}</p>",
            unsafe_allow_html=True,
        )

    if st.button("Sign in", type="primary", key="login_btn"):
        if not email or not password:
            st.session_state.login_error = "Please enter both email and password."
            st.rerun()
        else:
            DEMO_USERS = {
                "exec@fintech.ai": ("password123", "C-Level Executives"),
                "finance@fintech.ai": ("password123", "Finance Manager"),
                "risk@fintech.ai": ("password123", "Risk Analyst"),
                "compliance@fintech.ai": ("password123", "Compliance Officer"),
                "ops@fintech.ai": ("password123", "Operations Manager"),
                "analyst@fintech.ai": ("password123", "Data Analyst"),
            }
            if email in DEMO_USERS and DEMO_USERS[email][0] == password:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.session_state.user_role = DEMO_USERS[email][1]
                st.session_state.login_error = ""
                st.switch_page("pages/chat.py")
            else:
                st.session_state.login_error = "Invalid email or password."
                st.rerun()

    st.markdown(
        "<p class='mute-text' style='text-align:center; margin-top:18px; font-size:14px;'>Demo accounts: exec / finance / risk / compliance / ops / analyst @fintech.ai · password: password123</p>",
        unsafe_allow_html=True,
    )
