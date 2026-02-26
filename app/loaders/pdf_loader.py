import re
from typing import List

import fitz  # PyMuPDF

from app.loaders.base_loader import BaseLoader
from app.schemas.common import StructuredBlock


class PdfLoader(BaseLoader):
    """
    Heuristic PDF loader that:
    - merges adjacent lines into paragraph-like blocks
    - detects probable headings
    - carries section_path forward for following paragraphs
    """

    def _is_blank(self, line: str) -> bool:
        return not line or not line.strip()

    def _normalize_line(self, line: str) -> str:
        # collapse whitespace but preserve text
        return re.sub(r"\s+", " ", line).strip()

    def _looks_like_heading(self, line: str) -> bool:
        t = self._normalize_line(line)
        if not t:
            return False

        # too long lines are usually paragraphs
        if len(t) > 120:
            return False

        # numbered headings e.g. "2.1 Scope", "1 Introduction"
        if re.match(r"^\d+(\.\d+)*\s+\S+", t):
            return True

        # all caps short lines
        if t.isupper() and len(t.split()) <= 12:
            return True

        # title-like short lines (avoid obvious sentences)
        words = t.split()
        if 1 <= len(words) <= 12:
            if not t.endswith("."):
                alpha_words = [w for w in words if any(ch.isalpha() for ch in w)]
                if alpha_words:
                    titleish = sum(1 for w in alpha_words if w[:1].isupper()) / len(alpha_words)
                    if titleish >= 0.6:
                        return True

        return False

    def _join_lines(self, lines: List[str]) -> str:
        """
        Merge lines into a paragraph, handling simple hyphenated line-breaks.
        """
        cleaned = [self._normalize_line(x) for x in lines if self._normalize_line(x)]
        if not cleaned:
            return ""

        out = cleaned[0]
        for nxt in cleaned[1:]:
            # de-hyphenate common PDF line wraps: "rev-" + "enue" => "revenue"
            if out.endswith("-") and nxt and nxt[0].isalnum():
                out = out[:-1] + nxt
            else:
                out += " " + nxt
        out = re.sub(r"\s+", " ", out).strip()
        return out

    def load(self, path: str) -> List[StructuredBlock]:
        pdf = fitz.open(path)
        blocks: List[StructuredBlock] = []

        global_block_idx = 0
        active_section: str | None = None

        for page_idx, page in enumerate(pdf):
            raw_text = page.get_text("text") or ""
            lines = raw_text.splitlines()

            paragraph_buffer: List[str] = []
            page_no = page_idx + 1

            def flush_paragraph():
                nonlocal global_block_idx, paragraph_buffer, blocks, active_section
                text = self._join_lines(paragraph_buffer)
                paragraph_buffer = []

                if not text:
                    return

                # basic list detection
                content_type = "list" if re.match(r"^[•\-\*\d]+\s+", text) else "paragraph"

                blocks.append(
                    StructuredBlock(
                        block_id=f"pdf_p{page_no}_b{global_block_idx}",
                        content=text,
                        content_type=content_type,
                        page_number=page_no,
                        section_path=active_section,
                    )
                )
                global_block_idx += 1

            for line in lines:
                raw_line = line.rstrip("\n")
                norm_line = self._normalize_line(raw_line)

                # blank line => paragraph boundary
                if self._is_blank(raw_line):
                    flush_paragraph()
                    continue

                # probable heading => flush paragraph, emit heading block, update active section
                if self._looks_like_heading(norm_line):
                    flush_paragraph()

                    active_section = norm_line
                    blocks.append(
                        StructuredBlock(
                            block_id=f"pdf_p{page_no}_h{global_block_idx}",
                            content=norm_line,
                            content_type="header",
                            page_number=page_no,
                            section_path=active_section,
                        )
                    )
                    global_block_idx += 1
                    continue

                # normal line => keep buffering
                paragraph_buffer.append(norm_line)

            # flush any trailing paragraph for the page
            flush_paragraph()

        return blocks