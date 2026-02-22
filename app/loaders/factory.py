import os
from .pdf_loader import PdfLoader
from .docx_loader import DocxLoader

def get_loader(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return PdfLoader()

    if ext == ".docx":
        return DocxLoader()

    raise ValueError("Unsupported file type")
