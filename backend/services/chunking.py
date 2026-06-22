from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.docstore.document import Document   old version of langchain used this import path for Document, but in newer versions it's from langchain_core.documents import Document
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

#checkign the working
if __name__== "__main__":
    # Example usage
    sample_docs = [
        Document(page_content="This is a long document that needs to be chunked.", metadata={"source": "doc1.txt"}),
        Document(page_content="Another lengthy document for testing the chunking functionality.", metadata={"source": "doc2.txt"}),
    ]
    chunked = chunk_documents(sample_docs)
    # print(f"Original documents: {len(sample_docs)}, Chunked documents: {len(chunked)}")
    for doc in chunked:
        print(f"Chunk from {doc.metadata['source']}: {doc.page_content[:50]}...")