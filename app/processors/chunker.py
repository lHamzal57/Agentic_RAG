from typing import List, Dict, Any

from app.schemas.common import StructuredBlock, ChunkRecord
from app.core.config import settings

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None


def _token_len(text: str) -> int:
    if _enc is None:
        return max(1, len(text) // 4)
    return len(_enc.encode(text))


def _chunk_text_token_based(text: str, size: int, overlap: int) -> List[str]:
    tokens = _enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + size
        chunks.append(_enc.decode(tokens[start:end]))
        if end >= len(tokens):
            break
        start = max(0, end - overlap)
    return chunks


def _chunk_text_char_based(text: str, size: int, overlap: int) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = max(0, end - overlap)
    return chunks


def _split_text(text: str, size: int, overlap: int) -> List[str]:
    if _enc is not None:
        return _chunk_text_token_based(text, size, overlap)
    return _chunk_text_char_based(text, size, overlap)


def _build_semantic_windows(blocks: List[StructuredBlock]) -> List[Dict[str, Any]]:
    """
    Build larger semantic windows using page + heading/section context.
    Windows are composed from adjacent paragraph/list blocks under same page+section.
    """
    windows: List[Dict[str, Any]] = []

    current_section: str | None = None
    current_page: int | None = None
    current_texts: List[str] = []

    def flush_window():
        nonlocal current_texts, current_page, current_section, windows
        if not current_texts:
            return
        text = "\n".join(t for t in current_texts if t and t.strip()).strip()
        current_texts = []
        if not text:
            return
        windows.append(
            {
                "page_number": current_page,
                "section_path": current_section,
                "content_type": "section_window" if current_section else "paragraph_window",
                "text": text,
            }
        )

    max_window_chars = settings.RAG_SEMANTIC_WINDOW_MAX_CHARS

    for b in blocks:
        if not b.content or not b.content.strip():
            continue

        # Heading updates section context and creates a new semantic window boundary
        if b.content_type == "header":
            flush_window()
            current_section = b.content.strip()
            current_page = b.page_number
            # Start next window with the header included for context
            current_texts = [f"[Section] {current_section}"]
            continue

        # If page changes, flush window (page+heading window rule)
        if current_page is None:
            current_page = b.page_number
        elif b.page_number != current_page:
            flush_window()
            current_page = b.page_number
            current_texts = [f"[Section] {current_section}"] if current_section else []

        # If block already has a section_path and it differs, flush and switch
        if b.section_path and b.section_path != current_section:
            flush_window()
            current_section = b.section_path
            current_page = b.page_number
            current_texts = [f"[Section] {current_section}"]

        # Append block content
        current_texts.append(b.content.strip())

        # Prevent giant semantic windows before chunk splitting
        if sum(len(x) for x in current_texts) >= max_window_chars:
            flush_window()
            current_texts = [f"[Section] {current_section}"] if current_section else []

    flush_window()
    return windows


def split_blocks_into_chunks(doc_id: str, blocks: List[StructuredBlock]) -> List[ChunkRecord]:
    chunk_records: List[ChunkRecord] = []
    chunk_index = 0

    size = settings.RAG_CHUNK_SIZE
    overlap = settings.RAG_CHUNK_OVERLAP

    windows = _build_semantic_windows(blocks)

    for w in windows:
        base_text = (w["text"] or "").strip()
        if not base_text:
            continue

        parts = _split_text(base_text, size=size, overlap=overlap)

        for part in parts:
            text = part.strip()
            if not text:
                continue

            # Repeat section prefix for retrieval robustness if available
            section_path = w.get("section_path")
            if section_path and not text.startswith("[Section]"):
                text = f"[Section] {section_path}\n{text}"

            chunk_records.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    text=text,
                    content_type=w.get("content_type", "paragraph_window"),
                    page_number=w.get("page_number"),
                    section_path=section_path,
                )
            )
            chunk_index += 1

    return chunk_records