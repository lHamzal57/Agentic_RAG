from typing import Optional

from app.workflows.base import BaseWorkflow
from app.core.config import settings
from prompts import test_review


class TestReviewWorkflow(BaseWorkflow):
    name = "TestReviewWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_REVIEW or settings.RAG_TOP_K}

    def default_question(self) -> str:
        return (
            "Review the test artifact (test cases/test review notes) for completeness against the document. "
            "Identify missing coverage, inconsistencies, and risks, and provide recommendations."
        )

    def build_retrieval_query(self, user_question: Optional[str]) -> str:
        base = (user_question or self.default_question()).strip()
        hints = (
            "coverage, traceability, missing, gap, incomplete, inconsistency, ambiguous, risk, "
            "negative case, edge case, validation, business rule, requirement mapping, redundancy, "
            "priority, severity, acceptance criteria"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str]) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_review.render_prompt(context=context, question=question)