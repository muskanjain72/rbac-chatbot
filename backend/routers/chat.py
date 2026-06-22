from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.chat_sessions import (
    append_message,
    create_session,
    get_session,
    list_sessions,
)
from backend.services.rag_service import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    user_role: str = "C-Level Executives"
    session_id: str | None = None


@router.get("/")
def home():
    return {"message": "FinSolve Chatbot API Running"}


@router.get("/sessions")
def get_sessions():
    return {"sessions": list_sessions()}


@router.post("/sessions")
def start_session():
    session = create_session()
    return session.to_summary()


@router.get("/sessions/{session_id}")
def read_session(session_id: str):
    session = get_session(session_id)
    if session is None:
        return {"detail": "Session not found", "messages": []}
    return session.to_detail()

@router.post("/chat")
def chat(request: ChatRequest):
    session = get_session(request.session_id) if request.session_id else None
    if session is None:
        session = create_session()

    append_message(session.id, "user", request.query)
    answer = generate_answer(request.query, request.user_role)
    append_message(session.id, "assistant", answer)
    return {
        "session_id": session.id,
        "query": request.query,
        "user_role": request.user_role,
        "answer": answer,
    }
