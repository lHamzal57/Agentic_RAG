from fastapi import APIRouter, Depends, HTTPException
from app.dependencies.chroma import get_chroma_collection
from app.dependencies.ollama import get_ollama_client
from app.services.rag_service import RagService
from app.schemas.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
async def query_document(
    payload: QueryRequest,
    collection = Depends(get_chroma_collection),
    ollama_client = Depends(get_ollama_client),
):
    try:
        rag_service = RagService(collection=collection, ollama_client=ollama_client)
        result = rag_service.answer_question(
            doc_id=payload.doc_id,
            question=payload.question,
            top_k=payload.top_k
        )
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")