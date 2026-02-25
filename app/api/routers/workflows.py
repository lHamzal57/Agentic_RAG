from fastapi import APIRouter, Depends, HTTPException,Query

from app.dependencies.chroma import get_chroma_collection
from app.dependencies.ollama import get_ollama_client
from app.services.workflow_rag_service import WorkflowRagService
from app.schemas.workflows import WorkflowType, WorkflowQueryResponse

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/query", response_model=WorkflowQueryResponse)
async def query_by_workflow(
    doc_id: str = Query(..., description="Document ID to query"),
    workflow: WorkflowType = Query(..., description="Workflow type"),
    question: str = Query(..., description="User question"),
    top_k: int | None = Query(None, ge=1, le=20, description="Optional retrieval top-k"),
    collection=Depends(get_chroma_collection),
    ollama_client=Depends(get_ollama_client),
):
    try:
        service = WorkflowRagService(collection=collection, ollama_client=ollama_client)
        result = service.answer(
            doc_id=doc_id,
            workflow=workflow,
            question=question,
            top_k=top_k,
        )
        return WorkflowQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow query failed: {str(e)}")