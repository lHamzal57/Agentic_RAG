from app.services.retrieval_service import RetrievalService
from app.processors.workflow_prompt_builder import build_workflow_prompt
from app.schemas.workflows import WorkflowType


class WorkflowRagService:
    def __init__(self, collection, ollama_client):
        if not hasattr(ollama_client, "generate"):
            raise TypeError("ollama_client must provide a generate(prompt=...) method")

        self.retrieval = RetrievalService(collection)
        self.ollama = ollama_client

    def answer(
        self,
        doc_id: str,
        workflow: WorkflowType,
        question: str,
        top_k: int | None = None
    ) -> dict:
        chunks = self.retrieval.retrieve(
            doc_id=doc_id,
            question=question,
            top_k=top_k
        )

        if not chunks:
            return {
                "doc_id": doc_id,
                "workflow": workflow,
                "answer": "No relevant content found for this document.",
                "chunks_used": [],
            }

        prompt = build_workflow_prompt(
            workflow=workflow,
            question=question,
            chunks=chunks
        )

        answer = self.ollama.generate(prompt=prompt)

        return {
            "doc_id": doc_id,
            "workflow": workflow,
            "answer": answer,
            "chunks_used": chunks,
        }