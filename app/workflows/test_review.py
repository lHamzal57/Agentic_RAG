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
            "Review the provided test cases against the BRD and identify missing coverage, "
            "inconsistencies, and quality risks."
        )

    def build_retrieval_query(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        base = (user_question or self.default_question()).strip()
        hints = "coverage, missing, gap, inconsistency, ambiguous, risk, validation, business rule, acceptance criteria"
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict], inputs: Optional[str] = None, extra: Optional[dict] = None) -> str:
        context = self.format_context(chunks)
        return test_review.render_prompt(context=context, question=question, inputs=inputs)