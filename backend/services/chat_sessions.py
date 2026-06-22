from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class ChatSession:
    id: str
    title: str = "New chat"
    messages: list[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_detail(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [message.__dict__ for message in self.messages],
        }


_SESSIONS: dict[str, ChatSession] = {}
_LOCK = Lock()


def create_session(title: str = "New chat") -> ChatSession:
    with _LOCK:
        session = ChatSession(id=str(uuid4()), title=title)
        _SESSIONS[session.id] = session
        return session


def list_sessions() -> list[dict]:
    with _LOCK:
        sessions = sorted(
            _SESSIONS.values(),
            key=lambda session: session.updated_at,
            reverse=True,
        )
        return [session.to_summary() for session in sessions]


def get_session(session_id: str) -> ChatSession | None:
    with _LOCK:
        return _SESSIONS.get(session_id)


def append_message(session_id: str, role: str, content: str) -> ChatSession:
    with _LOCK:
        session = _SESSIONS.get(session_id)
        if session is None:
            session = ChatSession(id=session_id)
            _SESSIONS[session_id] = session

        session.messages.append(ChatMessage(role=role, content=content))
        session.updated_at = _now_iso()
        if role == "user" and session.title == "New chat":
            session.title = content.strip()[:28] or "New chat"
        return session
