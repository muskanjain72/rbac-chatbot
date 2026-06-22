import streamlit as st

st.set_page_config(page_title="fintechAI", layout="wide")

if st.session_state.get("authenticated"):
    st.switch_page("pages/chat.py")
else:
    st.switch_page("pages/login.py")
