from typing import Optional
from app.workflows.base import BaseWorkflow
from app.core.config import settings
from prompts import test_plan


class TestPlanWorkflow(BaseWorkflow):
    name = "TestPlanWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_PLAN or settings.RAG_TOP_K}

    def default_question(self) -> str:
        return (
            "Create a comprehensive test plan covering all business use cases, requirements, "
            "critical flows, validations, and acceptance criteria in the document."
        )

    def build_retrieval_query(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        base = (user_question or self.default_question()).strip()
        hints = (
            "business use case, user flow, requirement, acceptance criteria, business rule, validation, "
            "scope, dependency, integration, risk, assumption, test strategy, environment"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict], inputs: Optional[str] = None, extra: Optional[dict] = None) -> str:
        context = self.format_context(chunks)
        use_cases = (extra or {}).get("use_cases")
        return test_plan.render_prompt(context=context, question=question, use_cases=use_cases)