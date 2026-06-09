import os
from pathlib import Path
from typing import Iterable

from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import langchain_community.embeddings.huggingface as huggingface_embeddings
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from backend.core.config import settings
from backend.services.chunking import chunk_documents
from backend.services.document_loader import load_documents

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "datastore/data"
VECTOR_STORE_DIR = REPO_ROOT / "datastore/vector_store"

ACCESS_METADATA = {
    "engineering_master_doc.md": ["Engineering Team", "C-Level Executives"],
    "financial_summary.md": ["Finance Team", "C-Level Executives"],
    "quarterly_financial_report.md": ["Finance Team", "C-Level Executives"],
    "employee_handbook.md": ["All"],
    "hr_data.csv": ["HR Team", "C-Level Executives"],
    "market_report_q4_2024.md": ["Marketing Team", "C-Level Executives"],
    "marketing_report_2024.md": ["Marketing Team", "C-Level Executives"],
    "marketing_report_q1_2024.md": ["Marketing Team", "C-Level Executives"],
    "marketing_report_q2_2024.md": ["Marketing Team", "C-Level Executives"],
    "marketing_report_q3_2024.md": ["Marketing Team", "C-Level Executives"],
}

_VECTOR_STORE: Chroma | None = None


def _normalize_role(role: str) -> str:
    return role.strip().lower()


def _allowed_roles_for_document(source_path: str) -> set[str]:
    allowed_roles = ACCESS_METADATA.get(Path(source_path).name, ["All"])
    return {_normalize_role(role) for role in allowed_roles}


def _document_is_accessible(document: Document, user_role: str) -> bool:
    allowed_roles = _allowed_roles_for_document(document.metadata.get("source", ""))
    normalized_role = _normalize_role(user_role)
    return "all" in allowed_roles or normalized_role in allowed_roles


# def _embeddings() -> OpenAIEmbeddings:
#     if not settings.openai_api_key:
#         raise RuntimeError("OPENAI_API_KEY is required to build or query the vector store.")
#     return OpenAIEmbeddings(api_key=settings.openai_api_key)

def _embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
def _load_chunked_documents() -> list[Document]:
    documents = load_documents(str(DATA_DIR))
    chunked_documents = chunk_documents(documents)

    for document in chunked_documents:
        source_filename = Path(document.metadata.get("source", "")).name
        document.metadata["allowed_roles"] = ACCESS_METADATA.get(source_filename, ["All"])

    return chunked_documents


def create_vector_store():
    """
    Load, chunk, annotate, and persist the document corpus in Chroma.
    """
    print("Loading documents...")
    chunked_documents = _load_chunked_documents()

    print("Creating vector store...")
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    vector_store = Chroma.from_documents(
        documents=chunked_documents,
        embedding=_embeddings(),
        persist_directory=str(VECTOR_STORE_DIR),
    )

    global _VECTOR_STORE
    _VECTOR_STORE = vector_store
    print("Vector store created successfully.")
    return vector_store


def get_vector_store() -> Chroma:
    global _VECTOR_STORE
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE

    if VECTOR_STORE_DIR.exists():
        _VECTOR_STORE = Chroma(
            persist_directory=str(VECTOR_STORE_DIR),
            embedding_function=_embeddings(),
        )
        return _VECTOR_STORE

    return create_vector_store()


def retrieve_documents(query: str, user_role: str, k: int = 4, fetch_k: int = 12) -> list[Document]:
    vector_store = get_vector_store()
    candidates = vector_store.similarity_search(query, k=fetch_k)
    accessible_documents: list[Document] = []

    for document in candidates:
        if _document_is_accessible(document, user_role):
            accessible_documents.append(document)
        if len(accessible_documents) >= k:
            break

    return accessible_documents


def _format_context(documents: Iterable[Document]) -> str:
    sections = []
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown source")
        sections.append(f"[{index}] Source: {source}\n{document.page_content}")
    return "\n\n".join(sections)


def generate_answer(query: str, user_role: str) -> str:
    documents = retrieve_documents(query, user_role)

    if not documents:
        return "I couldn't find any accessible documents relevant to that question."

    context = _format_context(documents)

    if not settings.openai_api_key:
        return (
            "I found relevant information, but OPENAI_API_KEY is not configured so I cannot generate a full answer.\n\n"
            f"Relevant context:\n{context[:2000]}"
        )

    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=settings.openai_api_key,
    )

    messages = [
        SystemMessage(
            # content=(
            #     "You are a secure internal assistant. Answer only using the provided context. "
            #     "If the answer is not supported by the context, say you do not have enough information. "
            #     "Never reveal content from documents the user role should not access."
            # )
            content=("""
You are FinSolve AI, a secure role-based enterprise assistant.

The system enforces Role-Based Access Control (RBAC). You must only answer using the retrieved context provided to you. Treat the retrieved context as the complete set of information available to the current user.

If information is not present in the retrieved context, do not infer, guess, or generate it.

If a user asks about data that is unavailable, restricted, or outside their access scope, respond:

'The requested information is not available in the documents accessible to your role.'

Always:
- Use only retrieved context.
- Cite source documents.
- Be concise and professional.
- Never reveal hidden, restricted, or inferred information.
- Never speculate about documents you cannot see.
"""
)
        ),
        HumanMessage(
            content=(
                f"User role: {user_role}\n"
                f"Question: {query}\n\n"
            )
        ),
    ]

    response = llm.invoke(messages)
    return response.content.strip()


if __name__ == "__main__":
    create_vector_store()
