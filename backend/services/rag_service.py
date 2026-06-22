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
#__file__ is the path to the current file (rag_service.py), so we go up two levels to get to the repo root, and then define paths for the data directory and vector store directory relative to the repo root.
# This ensures that the service can reliably locate its data and vector store regardless of where it's run from.
DATA_DIR = REPO_ROOT / "datastore/data"
VECTOR_STORE_DIR = REPO_ROOT / "datastore/vector_store"

#control mapping of document filename to allowed roles. If a document is not listed here, it defaults to ["All"] which means it's accessible to all roles. 
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

#Instead of using open AIs paid API to generate embeddigns, we can use a free HuggingFace model to generate embeddings locally. 
# The "sentence-transformers/all-MiniLM-L6-v2" model is a popular choice for generating sentence embeddings and is efficient for many applications.

#creates an embedding model instance using HuggingFaceEmbeddings with the specified model name. 
def _embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
def _load_chunked_documents() -> list[Document]:  #returns a list of Document objects where each document's page_content is a chunk of the original content, and metadata is preserved and annotated with allowed_roles based on ACCESS_METADATA mapping.
    documents = load_documents(str(DATA_DIR))  #load the documents from the data directory using the custom load_documents function, which reads supported file types and creates Document objects with metadata.
    chunked_documents = chunk_documents(documents)  #chunk the loaded documents into smaller pieces using the chunk_documents function, which uses RecursiveCharacterTextSplitter to split the content while preserving metadata.

    for document in chunked_documents:
        #for each chunk in chunked_documents, we determine the allowed roles based on the source document's filename. 
        # We extract the filename from the source path in the document's metadata and look it up in the ACCESS_METADATA mapping to get the list of allowed roles.
        # This list is then stored in the document's metadata under the "allowed_roles" key for easy access during retrieval.
        source_filename = Path(document.metadata.get("source", "")).name
        document.metadata["allowed_roles"] = ACCESS_METADATA.get(source_filename, ["All"])
        #if nothing specified in ACCESS_METADATA for a document, it defaults to ["All"], meaning it's accessible to all roles.

    return chunked_documents


def create_vector_store():
    """
    Load, chunk, annotate, and persist the document corpus in Chroma.
    """
    print("Loading documents...")
    chunked_documents = _load_chunked_documents()

    print("Creating vector store...")
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
    #creates a Chroma vector store from the chunked documents, using the specified embeddings function and persisting it to the VECTOR_STORE_DIR.
    #for each document create embeddings using the HuggingFaceEmbeddings model, and store those embeddings in the Chroma vector store along with the document content and metadata. 
    # The vector store is then saved to disk so it can be loaded quickly in the future without needing to reprocess the documents.
    
    #chroma stores internally the document content, metadata, and the generated embeddings for each document chunk. This allows for efficient similarity search later when we want to retrieve relevant documents based on a user query.
    #u want to return the original text after similarity search 
    #with persisit dictionary, the vector store is saved to disk at the specified location, 
    # so subsequent runs can load the existing vector store without needing to reprocess the documents, which improves performance.
    vector_store = Chroma.from_documents(
        documents=chunked_documents,
        embedding=_embeddings(),
        persist_directory=str(VECTOR_STORE_DIR),
    )


    global _VECTOR_STORE
    _VECTOR_STORE = vector_store
    print("Vector store created successfully.")
    return vector_store


def get_vector_store() -> Chroma:  #returns the existing Chroma vector store if it has already been created and loaded, otherwise it checks if a persisted vector store exists on disk and loads it. 
    #If neither condition is met, it creates a new vector store from the documents.
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
    #fetch first k relevant chunks based on similarity search, but then we will filter these candidates based on access control to ensure we only return documents that the user's role is allowed to access.
    accessible_documents: list[Document] = [] 

    for document in candidates:
        if _document_is_accessible(document, user_role):
            accessible_documents.append(document)
        if len(accessible_documents) >= k:
            break
    #we need only 4 docs, but we are retrievng first 12 docs

    return accessible_documents


def _format_context(documents: Iterable[Document]) -> str:
    sections = []
    for index, document in enumerate(documents, start=1):
        source = document.metadata.get("source", "unknown source")
        sections.append(f"[{index}] Source: {source}\n{document.page_content}")
    return "\n\n".join(sections)
#joins all the strings 
    """[
    "[1] Source: employee_handbook.md\nEmployees get 20 annual leaves.",

    "[2] Source: employee_handbook.md\nReimbursement limit is ₹20,000."
        ]
    contains smthg like this, and then we join them with \n\n to create a single context string that can be fed into the LLM for answer generation.
    """


def generate_answer(query: str, user_role: str) -> str:
    documents = retrieve_documents(query, user_role)

    if not documents:
        return "I couldn't find any accessible documents relevant to that question. Or the documents that are relevant to your query are not accessible based on your role. Please try asking something else or contact your administrator if you believe you should have access to certain information."

    context = _format_context(documents)  #formating the docs

    if not settings.openai_api_key:
        return (
            "I found relevant information, but OPENAI_API_KEY is not configured so I cannot generate a full answer.\n\n"
            f"Relevant context:\n{context[:2000]}"
        )
        
    #creates llm client object
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
            """)
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
