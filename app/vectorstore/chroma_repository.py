from typing import List, Dict, Any
from app.schemas.common import ChunkRecord


class ChromaRepository:
    def __init__(self, collection):
        self.collection = collection
        
    @staticmethod
    def _sanitize_metadata(metadata: dict) -> dict:
        clean = {}
        for k, v in metadata.items():
            if v is None:
                continue  # Chroma does not accept None
            if isinstance(v, (str, int, float, bool)):
                clean[k] = v
            else:
                # fallback: convert unsupported values to string
                clean[k] = str(v)
        return clean
    
    # def add_chunks(self, chunks: List[ChunkRecord]) -> int:
    #     if not chunks:
    #         return 0

    #     self.collection.add(
    #         ids=[c.chunk_id for c in chunks],
    #         documents=[c.text for c in chunks],
    #         metadatas=[
    #             {
    #                 "doc_id": c.doc_id,
    #                 "chunk_index": c.chunk_index,
    #                 "content_type": c.content_type,
    #                 "page_number": c.page_number,
    #                 "section_path": c.section_path,
    #             }
    #             for c in chunks
    #         ],
    #     )
    #     return len(chunks)

    def add_chunks(self, chunks: List[ChunkRecord]) -> int:
        if not chunks:
            return 0

        metadatas = []
        for c in chunks:
            md = {
                "doc_id": c.doc_id,
                "chunk_index": c.chunk_index,
                "content_type": c.content_type,
                "page_number": c.page_number,
                "section_path": c.section_path,
            }
            metadatas.append(self._sanitize_metadata(md))

        print("Sample metadata:", metadatas[:3])

        self.collection.add(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            metadatas=metadatas,
        )
        return len(chunks)

    def query_by_doc(self, doc_id: str, query_text: str, n_results: int) -> List[Dict[str, Any]]:        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where={"doc_id": doc_id},
        )

        ids = results.get("ids", [[]])[0]
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

        items = []
        for i in range(len(ids)):
            items.append({
                "id": ids[i],
                "text": docs[i],
                "metadata": metas[i] if i < len(metas) else {},
            })
        return items
    
    def get_doc_chunks(self, doc_id: str, limit: int | None = None) -> Dict[str, Any]:
        # Chroma .get() supports filtering by metadata
        result = self.collection.get(
            where={"doc_id": doc_id},
            include=["metadatas"]  # ids are returned by default
        )

        ids = result.get("ids", []) or []
        metadatas = result.get("metadatas", []) or []

        if limit is not None and limit >= 0:
            ids = ids[:limit]
            metadatas = metadatas[:limit]

        return {
            "ids": ids,
            "metadatas": metadatas
        }

    def count_doc_chunks(self, doc_id: str) -> int:
        result = self.collection.get(
            where={"doc_id": doc_id},
            include=[]  # just ids is enough
        )
        return len(result.get("ids", []) or [])