import logging
from typing import Optional

from app.services.retrieval_service import RetrievalService
from app.schemas.workflows import WorkflowType
from app.workflows.registry import get_workflow_strategy
from app.core.config import settings
from prompts import user_stories as use_cases_prompt


logger = logging.getLogger(__name__)

# very simple in-memory cache (POC)
_USECASES_CACHE: dict[str, str] = {}


class WorkflowRagService:
    def __init__(self, collection, ollama_client):
        if not hasattr(ollama_client, "generate"):
            raise TypeError("ollama_client must provide a generate(prompt=...) method")

        self.retrieval = RetrievalService(collection)
        self.ollama = ollama_client

    def _get_or_generate_use_cases(self, doc_id: str) -> Optional[str]:
        if settings.RAG_USECASES_CACHE_ENABLED and doc_id in _USECASES_CACHE:
            return _USECASES_CACHE[doc_id]

        # retrieval query specifically for use-case extraction
        retrieval_query = (
            "Extract business use cases, user flows, actors/roles, and business scenarios from the document. "
            "Look for sections like Use Case, Scope, Business Flow, Requirements, User Journey."
        )

        chunks = self.retrieval.retrieve(
            doc_id=doc_id,
            question=retrieval_query,
            top_k=settings.RAG_USECASES_TOP_K,
        )

        if not chunks:
            return None

        context = "\n\n".join(f"[Chunk ID: {c['id']}]\n{c['text']}" for c in chunks)
        prompt = use_cases_prompt.render_prompt(context=context)
        use_cases_text = self.ollama.generate(prompt=prompt).strip()

        if settings.RAG_USECASES_CACHE_ENABLED and use_cases_text:
            _USECASES_CACHE[doc_id] = use_cases_text

        return use_cases_text or None

    def answer(
        self,
        doc_id: str,
        workflow: WorkflowType,
        question: Optional[str],
        top_k: int | None = None,
        inputs: Optional[str] = None,
        use_cases: Optional[str] = None,
    ) -> dict:
        strategy = get_workflow_strategy(workflow)

        user_question = (question or "").strip() or None
        user_inputs = (inputs or "").strip() or None

        extra: dict = {}

        # ---- Pre-step: for TestCasesWorkflow, derive use cases from doc if not provided
        if workflow == WorkflowType.TestCasesWorkflow and not use_cases and settings.RAG_TESTCASES_AUTOGEN_USECASES:
            derived = self._get_or_generate_use_cases(doc_id)
            if derived:
                extra["use_cases"] = derived
        else:
            if use_cases:
                extra["use_cases"] = use_cases.strip()

        retrieval_query = strategy.build_retrieval_query(user_question, extra=extra)
        prompt_question = strategy.build_prompt_question(user_question, extra=extra)

        workflow_default_top_k = strategy.retrieval_config().get("top_k")
        effective_top_k = top_k if top_k is not None else workflow_default_top_k

        logger.info(
            "workflow_rag_request | workflow=%s | doc_id=%s | effective_top_k=%s | has_user_question=%s | has_inputs=%s | has_usecases=%s",
            workflow.value,
            doc_id,
            effective_top_k,
            user_question is not None,
            user_inputs is not None,
            bool(extra.get("use_cases")),
        )

        chunks = self.retrieval.retrieve(
            doc_id=doc_id,
            question=retrieval_query,
            top_k=effective_top_k,
        )

        if not chunks:
            return {
                "doc_id": doc_id,
                "workflow": workflow,
                "answer": "No relevant content found for this document.",
                "chunks_used": [],
            }

        prompt = strategy.build_prompt(
            question=prompt_question,
            chunks=chunks,
            inputs=user_inputs,
            extra=extra,
        )

        raw_answer = self.ollama.generate(prompt=prompt)
        answer = strategy.postprocess(raw_answer)

        return {
            "doc_id": doc_id,
            "workflow": workflow,
            "answer": answer,
            "chunks_used": chunks,
        }