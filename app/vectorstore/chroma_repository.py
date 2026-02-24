from typing import List, Dict, Any
from datetime import date, datetime
import json

from app.schemas.common import ChunkRecord


class ChromaRepository:
    def __init__(self, collection):
        self.collection = collection

    @staticmethod
    def _sanitize_metadata_value(value: Any):
        """
        Chroma metadata supports scalar values only.
        Convert unsupported values to string/JSON and drop None upstream.
        """
        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        # Convert list/dict/tuple/set/... to JSON string if possible
        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except Exception:
            return str(value)

    @classmethod
    def _sanitize_metadata(cls, metadata: dict) -> dict:
        clean = {}
        for k, v in metadata.items():
            sanitized = cls._sanitize_metadata_value(v)
            if sanitized is None:
                continue  # Chroma rejects None in metadata
            clean[k] = sanitized
        return clean

    @staticmethod
    def _is_non_empty_text(text: str) -> bool:
        return isinstance(text, str) and bool(text.strip())

    def add_chunks(self, chunks: List[ChunkRecord], use_upsert: bool = True) -> int:
        """
        Adds/upserts chunks after sanitization.
        - Filters empty text chunks
        - Sanitizes metadata
        - Uses upsert by default to allow re-indexing same doc_id
        Returns number of chunks actually written.
        """
        if not chunks:
            return 0

        valid_chunks: List[ChunkRecord] = []
        for c in chunks:
            if not self._is_non_empty_text(c.text):
                continue
            valid_chunks.append(c)

        if not valid_chunks:
            return 0

        ids = [c.chunk_id for c in valid_chunks]
        documents = [c.text.strip() for c in valid_chunks]
        metadatas = [
            self._sanitize_metadata(
                {
                    "doc_id": c.doc_id,
                    "chunk_index": c.chunk_index,
                    "content_type": c.content_type,
                    "page_number": c.page_number,
                    "section_path": c.section_path,
                }
            )
            for c in valid_chunks
        ]

        payload = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }

        if use_upsert and hasattr(self.collection, "upsert"):
            self.collection.upsert(**payload)
        else:
            # Fallback if upsert not available in your Chroma version
            # (or if you explicitly disable use_upsert)
            self.collection.add(**payload)

        return len(valid_chunks)

    def delete_doc_chunks(self, doc_id: str) -> int:
        """
        Delete all chunks for a specific document.
        Useful before full re-index if you want strict replacement semantics.
        Returns best-effort deleted count (count before delete).
        """
        existing = self.collection.get(where={"doc_id": doc_id}, include=[])
        ids = existing.get("ids", []) or []
        if not ids:
            return 0

        self.collection.delete(where={"doc_id": doc_id})
        return len(ids)

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
            items.append(
                {
                    "id": ids[i],
                    "text": docs[i],
                    "metadata": metas[i] if i < len(metas) else {},
                }
            )
        return items

    def get_doc_chunks(self, doc_id: str, limit: int | None = None, include_docs: bool = False) -> Dict[str, Any]:
        include_fields = ["metadatas"]
        if include_docs:
            include_fields.append("documents")

        result = self.collection.get(
            where={"doc_id": doc_id},
            include=include_fields,
        )

        ids = result.get("ids", []) or []
        metadatas = result.get("metadatas", []) or []
        documents = result.get("documents", []) or []

        if limit is not None and limit >= 0:
            ids = ids[:limit]
            metadatas = metadatas[:limit]
            documents = documents[:limit] if documents else []

        out = {
            "ids": ids,
            "metadatas": metadatas,
        }
        if include_docs:
            out["documents"] = documents
        return out

    def count_doc_chunks(self, doc_id: str) -> int:
        result = self.collection.get(where={"doc_id": doc_id}, include=[])
        return len(result.get("ids", []) or [])