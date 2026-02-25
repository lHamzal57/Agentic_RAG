from app.services.retrieval_service import RetrievalService
from app.schemas.workflows import WorkflowType
from app.workflows.registry import get_workflow_strategy

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
        strategy = get_workflow_strategy(workflow)

        # workflow default top_k if caller didn't provide one
        effective_top_k = top_k
        if effective_top_k is None:
            effective_top_k = strategy.retrieval_config().get("top_k")

        chunks = self.retrieval.retrieve(
            doc_id=doc_id,
            question=question,
            top_k=effective_top_k
        )

        if not chunks:
            return {
                "doc_id": doc_id,
                "workflow": workflow,
                "answer": "No relevant content found for this document.",
                "chunks_used": [],
            }

        prompt = strategy.build_prompt(question=question, chunks=chunks)
        raw_answer = self.ollama.generate(prompt=prompt)
        answer = strategy.postprocess(raw_answer)

        return {
            "doc_id": doc_id,
            "workflow": workflow,
            "answer": answer,
            "chunks_used": chunks,
        }