from pydantic import BaseModel
from typing import Any

class UploadFileResponse(BaseModel):
    doc_id: str
    filename: str
    saved_path: str
    chunks_indexed: int


class FileStatusResponse(BaseModel):
    doc_id: str
    status: str  # indexed | not_found
    chunks_count: int
    sample_chunk_ids: list[str] = []

class ChunkPreview(BaseModel):
    id: str
    metadata: dict[str, Any]
    text_preview: str | None = None


class FileChunksResponse(BaseModel):
    doc_id: str
    chunks_count: int
    chunks: list[ChunkPreview]