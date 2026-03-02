from typing import Optional

from app.workflows.base import BaseWorkflow
from app.core.config import settings
from prompts import general_question


class GeneralQuestionWorkflow(BaseWorkflow):
    name = "GeneralQuestionWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_GENERAL_QUESTION or settings.RAG_TOP_K}

    def default_question(self) -> str:
        return (
            "Summarize the document and extract the key business requirements, scope, "
            "main features, constraints, assumptions, and any non-functional requirements."
        )

    def build_retrieval_query(self, user_question: Optional[str]) -> str:
        base = (user_question or self.default_question()).strip()
        hints = (
            "summary, overview, purpose, scope, objectives, requirements, business rules, "
            "constraints, assumptions, non-functional requirements, actors, workflows, dependencies"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str]) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return general_question.render_prompt(context=context, question=question)