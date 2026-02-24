from typing import List
from app.schemas.common import StructuredBlock, ChunkRecord
from app.core.config import settings

try:
    import tiktoken
    _enc = tiktoken.get_encoding("cl100k_base")
except Exception:
    _enc = None


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


def split_blocks_into_chunks(doc_id: str, blocks: List[StructuredBlock]) -> List[ChunkRecord]:
    chunk_records: List[ChunkRecord] = []
    chunk_index = 0

    size = settings.RAG_CHUNK_SIZE
    overlap = settings.RAG_CHUNK_OVERLAP

    for b in blocks:
        parts = (
            _chunk_text_token_based(b.content, size, overlap)
            if _enc is not None
            else _chunk_text_char_based(b.content, size, overlap)
        )

        for part in parts:
            chunk_records.append(
                ChunkRecord(
                    chunk_id=f"{doc_id}_chunk_{chunk_index}",
                    doc_id=doc_id,
                    chunk_index=chunk_index,
                    text=part,
                    content_type=b.content_type,
                    page_number=b.page_number,
                    section_path=b.section_path,
                )
            )
            chunk_index += 1

    return chunk_records