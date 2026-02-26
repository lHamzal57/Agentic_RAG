from app.vectorstore.chroma_repository import ChromaRepository


class FileInspectionService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    def list_chunks(self, doc_id: str, limit: int = 10, include_text: bool = False) -> dict:
        if limit < 1:
            limit = 1
        if limit > 100:
            limit = 100  # safety cap

        result = self.repo.get_doc_chunks(
            doc_id=doc_id,
            limit=limit,
            include_docs=include_text,   # only fetch documents when requested
        )

        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])
        documents = result.get("documents", []) if include_text else []

        chunks = []
        for i, chunk_id in enumerate(ids):
            text_preview = None
            if include_text:
                text = documents[i] if i < len(documents) else ""
                text_preview = (text[:250] + "...") if text and len(text) > 250 else text

            chunks.append(
                {
                    "id": chunk_id,
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "text_preview": text_preview,
                }
            )
            
        chunks.sort(key=lambda c: c.get("metadata", {}).get("chunk_index", 10**9))

        total = self.repo.count_doc_chunks(doc_id)

        return {
            "doc_id": doc_id,
            "chunks_count": total,
            "chunks": chunks,
        }