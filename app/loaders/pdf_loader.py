import fitz  # PyMuPDF
from typing import List
from app.loaders.base_loader import BaseLoader
from app.schemas.common import StructuredBlock


class PdfLoader(BaseLoader):
    def load(self, path: str) -> List[StructuredBlock]:
        pdf = fitz.open(path)
        blocks: List[StructuredBlock] = []

        for page_idx, page in enumerate(pdf):
            text = page.get_text("text")
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

            for line_idx, line in enumerate(lines):
                # basic heuristic; upgrade later to layout-aware extraction
                blocks.append(
                    StructuredBlock(
                        block_id=f"pdf_p{page_idx+1}_l{line_idx}",
                        content=line,
                        content_type="paragraph",
                        page_number=page_idx + 1,
                        section_path=None,
                    )
                )

        return blocks