from app.vectorstore.chroma_repository import ChromaRepository


class FileStatusService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    def get_status(self, doc_id: str) -> dict:
        count = self.repo.count_doc_chunks(doc_id)

        if count == 0:
            return {
                "doc_id": doc_id,
                "status": "not_found",
                "chunks_count": 0,
                "sample_chunk_ids": [],
            }

        sample = self.repo.get_doc_chunks(doc_id=doc_id, limit=5)

        return {
            "doc_id": doc_id,
            "status": "indexed",
            "chunks_count": count,
            "sample_chunk_ids": sample.get("ids", []),
        }