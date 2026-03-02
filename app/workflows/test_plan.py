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

    def build_retrieval_query(self, user_question: Optional[str]) -> str:
        # Query rewrite to improve semantic recall in vector search
        base = user_question or self.default_question()
        hints = (
            "business use case, user flow, requirement, acceptance criteria, business rule, "
            "validation, constraint, scope, dependency, integration, risk, assumption, "
            "edge case, negative case, test strategy, test environment"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str]) -> str:
        # What the model should actually answer
        return user_question or self.default_question()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_plan.render_prompt(context=context, question=question)