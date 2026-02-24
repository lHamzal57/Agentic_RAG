import os
from app.loaders.docx_loader import DocxLoader
from app.loaders.pdf_loader import PdfLoader
from app.loaders.base_loader import BaseLoader


def get_loader(file_path: str) -> BaseLoader:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".docx":
        return DocxLoader()
    if ext == ".pdf":
        return PdfLoader()

    raise ValueError(f"Unsupported file extension: {ext}")