from typing import Optional

from app.workflows.base import BaseWorkflow
from app.core.config import settings
from prompts import system_architecture


class SystemArchitectureWorkflow(BaseWorkflow):
    name = "SystemArchitectureWorkflow"

    def retrieval_config(self) -> dict:
        return {"top_k": settings.RAG_TOP_K_SYSTEM_ARCHITECTURE or settings.RAG_TOP_K}

    def default_question(self) -> str:
        return (
            "Extract the system architecture described in the document, including components/services, "
            "integrations/interfaces, data flows, storage/databases, and key constraints."
        )

    def build_retrieval_query(self, user_question: Optional[str]) -> str:
        base = (user_question or self.default_question()).strip()
        hints = (
            "architecture, component, service, module, microservice, API, endpoint, interface, "
            "integration, dependency, upstream, downstream, data flow, sequence, event, queue, "
            "database, storage, cache, authentication, authorization, SSO, encryption, network, protocol"
        )
        return f"{base}\n\nFocus terms: {hints}"

    def build_prompt_question(self, user_question: Optional[str]) -> str:
        return (user_question or self.default_question()).strip()

    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.format_context(chunks)
        return system_architecture.render_prompt(context=context, question=question)