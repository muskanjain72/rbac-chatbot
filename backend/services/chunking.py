from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.docstore.document import Document
from langchain_core.documents import Document

def chunk_documents(documents: list[Document]):
    """
    Splits a list of documents into smaller chunks using RecursiveCharacterTextSplitter.

    Args:
        documents: A list of documents to be chunked.

    Returns:
        A list of chunked documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunked_docs = text_splitter.split_documents(documents)
    return chunked_docs  #returns a list of Document objects where each document's page_content is a chunk of the original content, and metadata is preserved.
