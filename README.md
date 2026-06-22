# Role-Based Access Control (RBAC) Chatbot

A powerful, secure, and context-aware chatbot that integrates Role-Based Access Control (RBAC) to ensure users only receive answers backed by the data they are authorized to access. 

This project leverages **FastAPI** for a robust backend, **Streamlit** for an intuitive user interface, and **LangChain** with **ChromaDB** for Document Processing and Retrieval-Augmented Generation (RAG).

## 🌟 Features

- **Role-Based Access Control (RBAC):** Restricts data access dynamically. A user role is attached to the session, and queries hit only the vector embeddings the user has permissions for.
- **Automated Document Processing:** Automatically parses Markdown, CSV, and text files from the `datastore/data` directory.
- **Smart Chunking:** Uses recursive character splitting to break down large documents, keeping the conversational context intact.
- **Vector Storage:** Utilizes **ChromaDB** and OpenAI Embeddings to allow high-speed and accurate semantic search.
- **Citation and Source Mapping:** Retains metadata dynamically so all generated responses can be properly cited and sourced.

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12+
- **Frontend:** Streamlit
- **AI/RAG:** LangChain, OpenAI Embeddings, ChromaDB, Unstructured
- **Package Management:** `uv` or `pip` (via `pyproject.toml`)

## 📂 Project Structure

```text
rbac-chatbot/
│
├── backend/                  # FastAPI backend server
│   ├── main.py               # Application entry point
│   ├── core/                 # App configurations
│   ├── routers/              # API Route handlers (e.g., chat.py)
│   └── services/             # Core business logic (chunking, loaders, rag_service)
│
├── datastore/                # Data and persistent storage
│   ├── data/                 # Raw documents (markdown, csv, txt)
│   └── vector_store/         # ChromaDB persistence directory
│
├── frontend/                 # Streamlit frontend app
│   └── app.py
│
├── tests/                    # Core test cases
├── pyproject.toml            # Dependencies and project metadata
└── README.md
```

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.12 or higher.
- OpenAI API Key.

### 2. Installation

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/muskanjain72/rbac-chatbot.git
cd rbac-chatbot

# Using generic pip (if standard virtual environment is used):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Environment Variables

Create a `.env` file in the root of the project and add your configurations:

```env
OPENAI_API_KEY="your-openai-api-key-here"
```

### 4. Create the Vector Store

Before running the application, you need to embed the documents and populate ChromaDB:

```bash
# Ensure you are at the project root
python backend/services/rag_service.py
```
This loads all files in `datastore/data`, assigns RBAC metadata based on the rules, chunks them, and creates your local vector database.

### 5. Running the Application

You can launch both the backend and frontend at the same time using two separate terminal windows.

**Start the Backend (FastAPI):**
```bash
# Run from the project root
uvicorn backend.main:app --reload
```
The API should now be running at `http://localhost:8000`.

**Start the Frontend (Streamlit):**
```bash
# In a new terminal, run from the project root
streamlit run frontend/app.py
```
The Streamlit app should now be running at `http://localhost:8501`.

## 🔒 Details on Role-Based Access

Metadata is assigned to each document based on the `datastore/data/metadata.txt` guidelines. 
For instance, the **Financial Summary** is restricted to `Finance Team` and `C-Level Executives`. The chatbot will block any semantic retrieval of financial documents if the logged-in role does not match these.

Allowed roles include:
- `Engineering Team`
- `Finance Team`
- `Marketing Team`
- `HR & People Analytics`
- `C-Level Executives`
- `All` (e.g., Employee Handbook)

