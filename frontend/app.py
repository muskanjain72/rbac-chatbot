import os
from uuid import uuid4

import requests
import streamlit as st


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
DEFAULT_ROLE = os.getenv("DEFAULT_USER_ROLE", "C-Level Executives")


st.set_page_config(page_title="fintechAI", layout="centered")

st.markdown(
    """
    <style>
        html, body, [class*="css"] {
            background: #000000 !important;
            color: #0b63ff !important;
        }
        .stApp {
            background: #000000;
            color: #0b63ff;
        }
        div[data-testid="stChatMessage"] {
            background: #000000 !important;
            border: 1px solid #0b63ff !important;
            border-radius: 8px;
            padding: 0.5rem 0.75rem;
        }
        div[data-testid="stChatMessage"] * {
            color: #0b63ff !important;
        }
        div[data-testid="stChatInput"] textarea,
        .stTextInput input {
            background: #000000 !important;
            color: #0b63ff !important;
            border: 1px solid #0b63ff !important;
        }
        div[data-testid="stChatInput"] {
            background: #000000 !important;
            border-top: 1px solid #0b63ff !important;
        }
        .stButton button {
            background: #0b63ff !important;
            color: #000000 !important;
            border: 1px solid #0b63ff !important;
        }
        .stButton button:hover {
            background: #000000 !important;
            color: #0b63ff !important;
        }
        [data-testid="stHeader"] {
            background: #000000 !important;
        }
        header, footer {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='color:#0b63ff; text-align:center; margin-bottom:0;'>fintechAI</h1>",
    unsafe_allow_html=True,
)


def _new_thread(title: str = "New chat") -> dict:
    return {
        "id": str(uuid4()),
        "title": title,
        "messages": [],
    }


if "threads" not in st.session_state:
    st.session_state.threads = [_new_thread("New chat")]

if "active_thread_id" not in st.session_state:
    st.session_state.active_thread_id = st.session_state.threads[0]["id"]

if "show_history" not in st.session_state:
    st.session_state.show_history = True


def _active_thread() -> dict:
    for thread in st.session_state.threads:
        if thread["id"] == st.session_state.active_thread_id:
            return thread
    st.session_state.active_thread_id = st.session_state.threads[0]["id"]
    return st.session_state.threads[0]


def _thread_title(messages: list[dict]) -> str:
    for message in messages:
        if message["role"] == "user" and message["content"].strip():
            return message["content"].strip()[:28]
    return "New chat"


def _start_new_chat() -> None:
    thread = _new_thread()
    st.session_state.threads.insert(0, thread)
    st.session_state.active_thread_id = thread["id"]
    st.rerun()


header_left, header_right = st.columns([4, 1])
with header_right:
    label = "Hide history" if st.session_state.show_history else "Show history"
    if st.button(label, use_container_width=True):
        st.session_state.show_history = not st.session_state.show_history
        st.rerun()

if st.session_state.show_history:
    history_col, chat_col = st.columns([1, 3], gap="large")
else:
    history_col, chat_col = None, st.container()

if st.session_state.show_history:
    with history_col:
        if st.button("New chat", use_container_width=True):
            _start_new_chat()

        st.markdown(
            "<div style='color:#0b63ff; margin:0.5rem 0 0.25rem 0;'>Previous chats</div>",
            unsafe_allow_html=True,
        )

        for thread in st.session_state.threads:
            active = thread["id"] == st.session_state.active_thread_id
            button_label = f"{'• ' if active else ''}{thread['title']}"
            if st.button(button_label, key=thread["id"], use_container_width=True):
                st.session_state.active_thread_id = thread["id"]
                st.rerun()


active_thread = _active_thread()

with chat_col:
    for message in active_thread["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

query = st.chat_input("Ask a question")

if query:
    active_thread = _active_thread()
    active_thread["messages"].append({"role": "user", "content": query})
    active_thread["title"] = _thread_title(active_thread["messages"])

    payload = {"query": query, "user_role": DEFAULT_ROLE}
    try:
        response = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
        response.raise_for_status()
        answer = response.json().get("answer", "No answer received")
    except requests.RequestException:
        answer = "Backend is not available right now."

    active_thread["messages"].append({"role": "assistant", "content": answer})

    with chat_col:
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            st.markdown(answer)
