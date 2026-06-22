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

#whenever i get a post request to the /chat endpoint with a JSON body containing the query and user_role, the chat function is called.

@router.post("/chat")
def chat(request: ChatRequest):
    answer = generate_answer(request.query, request.user_role)
    return {
        "query": request.query,
        "user_role": request.user_role,
        "answer": answer,
    }
