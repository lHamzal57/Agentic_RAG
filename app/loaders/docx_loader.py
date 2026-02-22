from docx import Document
from .base_loader import BaseLoader

class DocxLoader(BaseLoader):
    def load(self, path: str):
        doc = Document(path)
        return "\n".join(
            p.text for p in doc.paragraphs if p.text.strip()
        )
