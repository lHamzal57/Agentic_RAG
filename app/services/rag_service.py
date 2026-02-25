from app.services.retrieval_service import RetrievalService
from app.processors.prompt_builder import build_rag_prompt
from app.clients.ollama_client import OllamaClient

class RagService:
    def __init__(self, collection, ollama_client: OllamaClient):
        if not hasattr(ollama_client, "generate"):
            raise TypeError("ollama_client must provide a generate(prompt=...) method")

        self.retrieval = RetrievalService(collection)
        self.ollama = ollama_client

    def answer_question(self, doc_id: str, question: str, top_k: int | None = None):
        chunks = self.retrieval.retrieve(doc_id=doc_id, question=question, top_k=top_k)

        if not chunks:
            return {
                "doc_id": doc_id,
                "answer": "No relevant content found for this document.",
                "chunks_used": []
            }
    
        prompt = build_rag_prompt(question=question, chunks=chunks)
        answer = self.ollama.generate(prompt=prompt)

        print("Ollama client type:", type(self.ollama))
        print("Has generate:", hasattr(self.ollama, "generate"))

        return {
            "doc_id": doc_id,
            "answer": answer,
            "chunks_used": chunks
        }