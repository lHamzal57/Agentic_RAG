from pydantic import BaseModel
from typing import Optional, Literal


class StructuredBlock(BaseModel):
    block_id: str
    content: str
    content_type: Literal["paragraph", "header", "list", "table", "figure_caption", "unknown"] = "paragraph"
    page_number: Optional[int] = None
    section_path: Optional[str] = None


class ChunkRecord(BaseModel):
    chunk_id: str
    doc_id: str
    chunk_index: int
    text: str
    content_type: str = "paragraph"
    page_number: Optional[int] = -1
    section_path: Optional[str] = ""