from app.workflows.base import BaseWorkflow
from prompts import test_review
from app.core.config import settings


class TestReviewWorkflow(BaseWorkflow):
    name = "TestReviewWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_REVIEW or settings.RAG_TOP_K}

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_review.render_prompt(context=context, question=question)