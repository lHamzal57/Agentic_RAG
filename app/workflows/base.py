from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseWorkflow(ABC):
    name: str = "BaseWorkflow"

    def retrieval_config(self) -> dict[str, Any]:
        return {}

    def default_question(self) -> str:
        return "Summarize the document."

    def build_retrieval_query(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        return user_question or self.default_question()

    def build_prompt_question(self, user_question: Optional[str], extra: Optional[dict] = None) -> str:
        return user_question or self.default_question()

    @staticmethod
    def format_context(chunks: list[dict]) -> str:
        if not chunks:
            return "(No relevant context found)"
        return "\n\n".join(f"[Chunk ID: {c['id']}]\n{c['text']}" for c in chunks)

    @abstractmethod
    def build_prompt(
        self,
        question: str,
        chunks: list[dict],
        inputs: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> str:
        raise NotImplementedError

    def postprocess(self, llm_answer: str) -> str:
        return llm_answer.strip()