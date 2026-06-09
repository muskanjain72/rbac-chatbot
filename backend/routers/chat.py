from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.rag_service import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    user_role: str


@router.get("/")
def home():
    return {"message": "FinSolve Chatbot API Running"}


@router.post("/")
def chat(request: ChatRequest):
    answer = generate_answer(request.query, request.user_role)
    return {
        "query": request.query,
        "user_role": request.user_role,
        "answer": answer,
    }
