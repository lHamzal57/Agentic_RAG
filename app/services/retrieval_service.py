from app.vectorstore.chroma_repository import ChromaRepository
from app.core.config import settings


class RetrievalService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    def _expand_neighbors(self, doc_id: str, chunks: list[dict]) -> list[dict]:
        if not chunks:
            return chunks

        if not settings.RAG_RETRIEVAL_EXPAND_NEIGHBORS:
            return chunks

        radius = max(0, settings.RAG_RETRIEVAL_NEIGHBOR_RADIUS)
        if radius == 0:
            return chunks

        # Pull doc chunks and build local index map (POC-friendly)
        full = self.repo.get_doc_chunks(doc_id=doc_id, include_docs=True)
        ids = full.get("ids", [])
        metadatas = full.get("metadatas", [])
        documents = full.get("documents", [])

        by_chunk_index = {}
        for i, chunk_id in enumerate(ids):
            md = metadatas[i] if i < len(metadatas) else {}
            txt = documents[i] if i < len(documents) else ""
            idx = md.get("chunk_index")
            if isinstance(idx, int):
                by_chunk_index[idx] = {
                    "id": chunk_id,
                    "text": txt,
                    "metadata": md,
                }

        selected_by_id = {c["id"]: c for c in chunks}

        for c in chunks:
            md = c.get("metadata", {}) or {}
            seed_idx = md.get("chunk_index")
            if not isinstance(seed_idx, int):
                continue

            for n in range(seed_idx - radius, seed_idx + radius + 1):
                neighbor = by_chunk_index.get(n)
                if not neighbor:
                    continue
                selected_by_id.setdefault(neighbor["id"], neighbor)

        expanded = list(selected_by_id.values())

        if settings.RAG_PROMPT_SORT_CHUNKS_BY_INDEX:
            expanded.sort(key=lambda x: (x.get("metadata", {}) or {}).get("chunk_index", 10**9))

        return expanded

    def retrieve(self, doc_id: str, question: str, top_k: int | None = None):
        # IMPORTANT: explicit None check (fixes top_k=0 fallback behavior)
        effective_top_k = top_k if top_k is not None else settings.RAG_TOP_K

        if effective_top_k < 1:
            raise ValueError("top_k must be >= 1")

        base_chunks = self.repo.query_by_doc(
            doc_id=doc_id,
            query_text=question,
            n_results=effective_top_k
        )

        return self._expand_neighbors(doc_id=doc_id, chunks=base_chunks)