from pydantic import BaseModel


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