from abc import ABC, abstractmethod
from typing import Any


class BaseWorkflow(ABC):
    """
    Strategy interface for workflow-specific RAG behavior.
    """

    name: str = "BaseWorkflow"

    def retrieval_config(self) -> dict[str, Any]:
        """
        Optional per-workflow retrieval tuning.
        Example: {"top_k": 8}
        """
        return {}

    @staticmethod
    def format_context(chunks: list[dict]) -> str:
        if not chunks:
            return "(No relevant context found)"
        return "\n\n".join(
            f"[Chunk ID: {c['id']}]\n{c['text']}" for c in chunks
        )

    @abstractmethod
    def build_prompt(self, question: str, chunks: list[dict]) -> str:
        raise NotImplementedError

    def postprocess(self, llm_answer: str) -> str:
        """
        Hook for cleanup/normalization if needed later.
        """
        return llm_answer.strip()