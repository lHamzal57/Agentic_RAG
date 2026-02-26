from pydantic import BaseModel, Field
from typing import List, Dict, Any


class QueryRequest(BaseModel):
    doc_id: str
    question: str
    top_k: int | None = Field(default=None, ge=1, le=50)

class QueryResponse(BaseModel):
    doc_id: str
    answer: str
    chunks_used: List[Dict[str, Any]]