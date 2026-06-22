import requests
import streamlit as st
from styles import BACKEND_URL


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{BACKEND_URL}{path}"
    r = requests.request(method, url, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()


def fetch_sessions() -> list[dict]:
    try:
        return _request("GET", "/sessions").get("sessions", [])
    except requests.RequestException:
        return []


def fetch_session(session_id: str) -> dict:
    try:
        return _request("GET", f"/sessions/{session_id}")
    except requests.RequestException:
        return {"id": session_id, "title": "New chat", "messages": []}


def create_session() -> dict:
    try:
        return _request("POST", "/sessions")
    except requests.RequestException:
        st.session_state._session_counter = getattr(st.session_state, "_session_counter", 0) + 1
        sid = f"local-{st.session_state._session_counter}"
        return {"id": sid, "title": "New chat"}


def send_message(query: str, user_role: str, session_id: str) -> tuple[str, str]:
    """Returns (answer, session_id)."""
    payload = {"query": query, "user_role": user_role, "session_id": session_id}
    try:
        r = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data.get("answer", "No answer received."), data.get("session_id", session_id)
    except requests.RequestException:
        return "⚠️ Backend is not available right now.", session_id


def ensure_active_session() -> None:
    """Bootstrap active_session_id on first load."""
    if "active_session_id" not in st.session_state:
        sessions = fetch_sessions()
        if sessions:
            st.session_state.active_session_id = sessions[0]["id"]
        else:
            created = create_session()
            st.session_state.active_session_id = created["id"]