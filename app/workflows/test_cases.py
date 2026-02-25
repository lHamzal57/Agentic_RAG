from app.workflows.base import BaseWorkflow
from prompts import test_cases
from app.core.config import settings


class TestCasesWorkflow(BaseWorkflow):
    name = "TestCasesWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_CASES or settings.RAG_TOP_K}

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_cases.render_prompt(context=context, question=question)