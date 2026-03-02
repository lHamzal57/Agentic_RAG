from typing import Optional

from app.workflows.base import BaseWorkflow
from app.core.config import settings
from prompts import test_cases


class TestCasesWorkflow(BaseWorkflow):
    name = "TestCasesWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_TEST_CASES or settings.RAG_TOP_K}

    def default_question(self) -> str:
        return (
            "Generate system test cases mapped to the requirements in the document, "
            "including positive/negative scenarios, validations, and expected results."
        )

    def build_retrieval_query(self, user_question: Optional[str]) -> str:
        base = (user_question or self.default_question()).strip()
        hints = (
            "requirement, shall, must, acceptance criteria, business rule, validation, constraint, "
            "scenario, user flow, precondition, postcondition, input, output, expected result, "
            "error handling, negative case, edge case, boundary values"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str]) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return test_cases.render_prompt(context=context, question=question)