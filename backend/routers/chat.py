from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    user_role: str


@router.post("/")
def chat(request: ChatRequest):
    return {
        "query": request.query,
        "user_role": request.user_role,
        "answer": "Placeholder response",
    }