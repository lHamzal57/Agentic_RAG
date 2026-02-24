from app.services.retrieval_service import RetrievalService
from app.processors.prompt_builder import build_rag_prompt


class RagService:
    def __init__(self, collection, ollama_client):
        self.retrieval = RetrievalService(collection)
        self.ollama = ollama_client

    def answer_question(self, doc_id: str, question: str, top_k: int | None = None):
        chunks = self.retrieval.retrieve(doc_id=doc_id, question=question, top_k=top_k)
        prompt = build_rag_prompt(question=question, chunks=chunks)
        answer = self.ollama.generate(prompt=prompt)

        return {
            "doc_id": doc_id,
            "answer": answer,
            "chunks_used": chunks
        }