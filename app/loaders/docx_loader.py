from docx import Document
from typing import List
from app.loaders.base_loader import BaseLoader
from app.schemas.common import StructuredBlock


class DocxLoader(BaseLoader):
    def load(self, path: str) -> List[StructuredBlock]:
        doc = Document(path)
        blocks: List[StructuredBlock] = []

        for i, p in enumerate(doc.paragraphs):
            text = (p.text or "").strip()
            if not text:
                continue

            # very basic heuristic (upgrade later)
            style_name = (p.style.name or "").lower() if p.style else ""
            content_type = "header" if "heading" in style_name else "paragraph"

            blocks.append(
                StructuredBlock(
                    block_id=f"docx_block_{i}",
                    content=text,
                    content_type=content_type,
                    page_number=None,
                    section_path=None,
                )
            )

        return blocks