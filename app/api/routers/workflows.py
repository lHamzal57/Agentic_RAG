from fastapi import APIRouter, Depends, HTTPException, Form

from app.dependencies.chroma import get_chroma_collection
from app.dependencies.ollama import get_ollama_client
from app.services.workflow_rag_service import WorkflowRagService
from app.schemas.workflows import (
    WorkflowQueryRequest,
    WorkflowQueryResponse,
    WorkflowType,
)

router = APIRouter(prefix="/workflows", tags=["workflows"])


def _run_workflow_query(
    payload: WorkflowQueryRequest,
    collection,
    ollama_client,
) -> WorkflowQueryResponse:
    service = WorkflowRagService(collection=collection, ollama_client=ollama_client)
    result = service.answer(
        doc_id=payload.doc_id,
        workflow=payload.workflow,
        question=payload.question,
        top_k=payload.top_k,
    )
    return WorkflowQueryResponse(**result)


# JSON body version (production-friendly)
@router.post("/query", response_model=WorkflowQueryResponse)
async def query_by_workflow_json(
    payload: WorkflowQueryRequest,
    collection=Depends(get_chroma_collection),
    ollama_client=Depends(get_ollama_client),
):
    try:
        return _run_workflow_query(payload, collection, ollama_client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow query failed: {str(e)}")


# Form version (Swagger-friendly separate input fields)
@router.post("/query-form", response_model=WorkflowQueryResponse)
async def query_by_workflow_form(
    doc_id: str = Form(..., description="Document ID"),
    workflow: WorkflowType = Form(..., description="Workflow type"),
    question: str = Form(..., description="Question / task request"),
    top_k: int | None = Form(None, description="Optional retrieval top-k override"),
    collection=Depends(get_chroma_collection),
    ollama_client=Depends(get_ollama_client),
):
    try:
        payload = WorkflowQueryRequest(
            doc_id=doc_id,
            workflow=workflow,
            question=question,
            top_k=top_k,
        )
        return _run_workflow_query(payload, collection, ollama_client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow query failed: {str(e)}")