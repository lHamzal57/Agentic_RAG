import fitz
from .base_loader import BaseLoader

class PdfLoader(BaseLoader):
    def load(self, path: str):
        pdf = fitz.open(path)
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
