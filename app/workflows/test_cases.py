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
            "Generate system test cases mapped to requirements and business use cases, "
            "including positive/negative scenarios, validations, and expected results."
        )

    def build_retrieval_query(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        base = (user_question or self.default_question()).strip()
        use_cases = (extra or {}).get("use_cases")
        hints = (
            "requirement, shall, must, acceptance criteria, business rule, validation, constraint, "
            "scenario, user flow, precondition, postcondition, expected result, error handling, "
            "negative case, edge case, boundary"
        )
        if use_cases:
            return f"{base}\n\nUse cases:\n{use_cases}\n\nFocus terms: {hints}"
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict], inputs: Optional[str] = None, extra: Optional[dict] = None) -> str:
        context = self.format_context(chunks)
        use_cases = (extra or {}).get("use_cases")
        return test_cases.render_prompt(context=context, question=question, use_cases=use_cases, inputs=inputs)