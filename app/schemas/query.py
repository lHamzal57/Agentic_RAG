from pydantic import BaseModel
from typing import List, Dict, Any


class QueryRequest(BaseModel):
    doc_id: str
    question: str
    top_k: int | None = None


class QueryResponse(BaseModel):
    doc_id: str
    answer: str
    chunks_used: List[Dict[str, Any]]