from backend.core.config import settings


class RAGService:
    def __init__(self) -> None:
        self.qdrant_url = settings.qdrant_url
        self.openai_api_key = settings.openai_api_key

    def answer(self, query: str, user_role: str) -> str:
        # TODO: add RBAC filtering, retrieval, and LLM generation
        return f"Stub response for role={user_role}: {query}"