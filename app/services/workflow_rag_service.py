import logging
from typing import Optional

from app.services.retrieval_service import RetrievalService
from app.schemas.workflows import WorkflowType
from app.workflows.registry import get_workflow_strategy

logger = logging.getLogger(__name__)


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
        question: Optional[str],
        top_k: int | None = None
    ) -> dict:
        strategy = get_workflow_strategy(workflow)

        # Normalize empty question -> None
        user_question = (question or "").strip() or None

        retrieval_query = strategy.build_retrieval_query(user_question)
        prompt_question = strategy.build_prompt_question(user_question)

        workflow_default_top_k = strategy.retrieval_config().get("top_k")
        effective_top_k = top_k if top_k is not None else workflow_default_top_k

        logger.info(
            "workflow_rag_request | workflow=%s | doc_id=%s | effective_top_k=%s | user_question=%s | retrieval_query_preview=%s",
            workflow.value if hasattr(workflow, "value") else str(workflow),
            doc_id,
            effective_top_k,
            user_question is not None,
            (retrieval_query[:160] + "...") if len(retrieval_query) > 160 else retrieval_query,
        )

        chunks = self.retrieval.retrieve(
            doc_id=doc_id,
            question=retrieval_query,   # <-- retrieval uses rewritten query
            top_k=effective_top_k
        )

        if not chunks:
            return {
                "doc_id": doc_id,
                "workflow": workflow,
                "answer": "No relevant content found for this document.",
                "chunks_used": [],
            }

        prompt = strategy.build_prompt(question=prompt_question, chunks=chunks)

        raw_answer = self.ollama.generate(prompt=prompt)
        answer = strategy.postprocess(raw_answer)

        return {
            "doc_id": doc_id,
            "workflow": workflow,
            "answer": answer,
            "chunks_used": chunks,
        }