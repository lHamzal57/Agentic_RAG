from app.vectorstore.chroma_repository import ChromaRepository
from app.core.config import settings


class RetrievalService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    def retrieve(self, doc_id: str, question: str, top_k: int | None = None):
        return self.repo.query_by_doc(
            doc_id=doc_id,
            query_text=question,
            n_results=top_k or settings.RAG_TOP_K
        )