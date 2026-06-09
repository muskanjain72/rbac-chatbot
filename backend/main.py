from fastapi import FastAPI
from backend.routers.chat import router as chat_router

app = FastAPI(title="RBAC Chatbot API", version="0.1.0")
app.include_router(chat_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}