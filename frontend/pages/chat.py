import streamlit as st
from styles import DESIGN_CSS, ROLES
from api import fetch_sessions, fetch_session, create_session, send_message, ensure_active_session

st.set_page_config(page_title="fintechAI", layout="wide")
st.markdown(DESIGN_CSS, unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.switch_page("pages/login.py")

ensure_active_session()

user_role = st.session_state.get("user_role", ROLES[0])
user_email = st.session_state.get("user_email", "user@fintech.ai")

with st.sidebar:
    st.markdown(
        "<div style='padding:8px 0 16px 0;'>"
        "<span style='font-size:22px;font-weight:400;letter-spacing:-0.65px;color:#ffffff;'>"
        "fintech<span style='color:#00d992;'>AI</span></span></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div class='role-pill'>Role: <span>{user_role}</span></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<hr class='green-divider'>", unsafe_allow_html=True)

    if st.button("＋  New chat", use_container_width=True, key="new_chat_btn"):
        created = create_session()
        st.session_state.active_session_id = created["id"]
        st.rerun()

    st.markdown("<div class='sidebar-label'>Previous chats</div>", unsafe_allow_html=True)

    sessions = fetch_sessions()
    if sessions and st.session_state.active_session_id not in {s["id"] for s in sessions}:
        st.session_state.active_session_id = sessions[0]["id"]

    if not sessions:
        st.markdown("<p class='mute-text' style='font-size:13px;'>No previous chats.</p>", unsafe_allow_html=True)
    else:
        for s in sessions:
            is_active = s["id"] == st.session_state.active_session_id
            label = f"{'● ' if is_active else '○ '}{s['title']}"
            btn_style = "border-color:#00d992 !important; color:#00d992 !important;" if is_active else ""
            st.markdown(
                f"<style>div[data-testid='stButton'] button[kind='secondary']#{s['id']} "
                f"{{ {btn_style} }}</style>",
                unsafe_allow_html=True,
            )
            if st.button(label, key=s["id"], use_container_width=True):
                st.session_state.active_session_id = s["id"]
                st.rerun()

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("<hr class='green-divider'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:12px; color:#8b949e; margin:4px 0;'>{user_email}</p>",
        unsafe_allow_html=True,
    )
    if st.button("Sign out", use_container_width=True, key="signout_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.switch_page("pages/login.py")

active_session = fetch_session(st.session_state.active_session_id)
messages = active_session.get("messages", [])

st.markdown(
    f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                border-bottom:1px solid #3d3a39; padding-bottom:12px; margin-bottom:16px;">
        <span style="font-size:20px; font-weight:600; letter-spacing:-0.6px; color:#ffffff;">
            {active_session.get('title', 'New chat')}
        </span>
        <div class='role-pill'>Role: <span>{user_role}</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not messages:
    st.markdown(
        """
        <div style="text-align:center; padding:80px 0 40px 0;">
            <p style="font-size:36px; font-weight:400; letter-spacing:-0.9px; color:#ffffff; margin-bottom:8px;">
                How can I help?
            </p>
            <p style="color:#8b949e; font-size:16px;">
                Ask me anything about your financial data, reports, or compliance queries.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

query = st.chat_input("Ask a question…")

if query:
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner(""):
            answer, new_sid = send_message(query, user_role, st.session_state.active_session_id)
        st.markdown(answer)
        st.session_state.active_session_id = new_sid

    st.rerun()
