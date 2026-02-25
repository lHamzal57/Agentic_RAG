from app.workflows.base import BaseWorkflow
from prompts import system_architecture
from app.core.config import settings


class SystemArchitectureWorkflow(BaseWorkflow):
    name = "SystemArchitectureWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_SYSTEM_ARCHITECTURE or settings.RAG_TOP_K}  # architecture often needs broader context

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return system_architecture.render_prompt(context=context, question=question)