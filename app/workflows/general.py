from app.workflows.base import BaseWorkflow
from prompts import general_question
from app.core.config import settings


class GeneralQuestionWorkflow(BaseWorkflow):
    name = "GeneralQuestionWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_GENERAL_QUESTION or settings.RAG_TOP_K}

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return general_question.render_prompt(context=context, question=question)