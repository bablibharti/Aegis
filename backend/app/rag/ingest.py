from pathlib import Path

from pypdf import PdfReader


def load_document(file_path: str) -> str:
    """
    Loads a .txt or .pdf file and returns its raw text content.
    """
    path = Path(file_path)

    if path.suffix == ".pdf":
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text

    if path.suffix == ".txt":
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Unsupported file type: {path.suffix}")
