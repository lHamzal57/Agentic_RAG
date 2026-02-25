from app.workflows.base import BaseWorkflow
from prompts import test_plan
from app.core.config import settings


class TestPlanWorkflow(BaseWorkflow):
    name = "TestPlanWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_PLAN or settings.RAG_TOP_K}  # planning usually benefits from wider scope

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_plan.render_prompt(context=context, question=question)