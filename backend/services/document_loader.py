
import csv
from pathlib import Path

from langchain_core.documents import Document

#supports only md, txt, and csv files for loading documents. This is to avoid the need for extra dependencies for markdown parsing and to keep the loading process simple and efficient.
SUPPORTED_SUFFIXES = {".md", ".txt", ".csv"}
REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore").strip()


def _read_csv_file(file_path: Path) -> str:
    with file_path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            return ""

        rows: list[str] = []
        for row in reader:
            row_text = ", ".join(f"{key}: {value}" for key, value in row.items() if key)
            if row_text:
                rows.append(row_text)

    if rows:
        header = ", ".join(reader.fieldnames)
        return f"Headers: {header}\n" + "\n".join(rows)

    return ""


def load_documents(path: str):
    """
    Load markdown, text, and CSV documents recursively from a directory.

    This avoids the optional `unstructured[md]` dependency used by
    `DirectoryLoader` for markdown parsing, so loading works in a minimal
    environment without extra installs.
    """
    #so basically Path returns a path object so that we can perform operations on it like checking if it exists, getting its absolute path, etc. expanduser() is used to expand the ~ to the user's home directory.
    base_path = Path(path).expanduser()
    if not base_path.is_absolute():
        base_path = (Path.cwd() / base_path).resolve()
        if not base_path.exists():
            base_path = (REPO_ROOT / path).resolve()
            #.resolve() is used to get the absolute path of the file, and it also resolves any symbolic links in the path. 
    else:
        base_path = base_path.resolve()
    if not base_path.exists():
        return []

    documents = []
    #rglob all files with supported suffixes, read content based on file type, and create Document objects with metadata (source and file_type)
    for file_path in sorted(p for p in base_path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES):
        if file_path.suffix.lower() == ".csv":
            content = _read_csv_file(file_path)
        else:
            content = _read_text_file(file_path)

        if not content:
            continue
        
        #document list consists of Document objects with page_content and metadata (source and file_type)
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "source": str(file_path),
                    "file_type": file_path.suffix.lower().lstrip("."),
                },
            )
        )

    return documents


if __name__ == "__main__":
    loaded_docs = load_documents("datastore/data")
    print(f"Loaded {len(loaded_docs)} documents.")
    for doc in loaded_docs:
        print(f"Source: {doc.metadata.get('source')}, Content Preview: {doc.page_content[:100]}...")
