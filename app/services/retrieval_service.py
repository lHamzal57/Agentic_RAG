import logging
import re
from typing import List, Dict, Any

from app.vectorstore.chroma_repository import ChromaRepository
from app.core.config import settings


logger = logging.getLogger(__name__)


class RetrievalService:
    def __init__(self, collection):
        self.repo = ChromaRepository(collection)

    # ---------------------------
    # Public API
    # ---------------------------
    def retrieve(self, doc_id: str, question: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        # Explicit None check (fixes top_k=0 fallback bug if schema validation is bypassed)
        effective_top_k = top_k if top_k is not None else settings.RAG_TOP_K
        if effective_top_k < 1:
            raise ValueError("top_k must be >= 1")

        candidate_k = self._candidate_k(effective_top_k)

        logger.info(
            "retrieval_request | doc_id=%s | top_k=%s | candidate_k=%s | rerank=%s",
            doc_id,
            effective_top_k,
            candidate_k,
            settings.RAG_RERANK_ENABLED,
        )

        # Step 1: retrieve larger candidate set from Chroma
        candidates = self.repo.query_by_doc(
            doc_id=doc_id,
            query_text=question,
            n_results=candidate_k,
        )

        logger.info(
            "retrieval_candidates | doc_id=%s | candidate_count=%s | candidate_ids=%s",
            doc_id,
            len(candidates),
            [c.get("id") for c in candidates],
        )

        # Step 2: rerank locally
        if settings.RAG_RERANK_ENABLED and candidates:
            seeds = self._rerank_candidates(question=question, candidates=candidates, final_top_k=effective_top_k)
        else:
            seeds = candidates[:effective_top_k]

        logger.info(
            "retrieval_seeds | doc_id=%s | seed_count=%s | seed_ids=%s",
            doc_id,
            len(seeds),
            [c.get("id") for c in seeds],
        )

        # Step 3: expand neighbors for context continuity
        expanded = self._expand_neighbors(doc_id=doc_id, chunks=seeds)

        logger.info(
            "retrieval_expanded | doc_id=%s | expanded_count=%s | expanded_ids=%s",
            doc_id,
            len(expanded),
            [c.get("id") for c in expanded],
        )

        return expanded

    # ---------------------------
    # Candidate sizing
    # ---------------------------
    def _candidate_k(self, final_top_k: int) -> int:
        mult = max(1, settings.RAG_RETRIEVAL_CANDIDATE_MULTIPLIER)
        cap = max(1, settings.RAG_RETRIEVAL_CANDIDATE_MAX)
        return min(cap, max(final_top_k, final_top_k * mult))

    # ---------------------------
    # Local reranking
    # ---------------------------
    def _rerank_candidates(self, question: str, candidates: List[Dict[str, Any]], final_top_k: int) -> List[Dict[str, Any]]:
        q_norm = self._normalize_text(question)
        q_terms = self._tokenize_for_matching(question)
        q_ngrams = self._query_ngrams(q_terms, n_values=(2, 3))

        scored = []
        for c in candidates:
            score_info = self._score_candidate(
                question_norm=q_norm,
                question_terms=q_terms,
                question_ngrams=q_ngrams,
                candidate=c,
                total_candidates=len(candidates),
            )
            c_with_score = dict(c)
            c_with_score["_rerank_score"] = score_info["score"]
            c_with_score["_score_breakdown"] = score_info
            scored.append(c_with_score)

        scored.sort(
            key=lambda x: (
                x.get("_rerank_score", 0.0),
                -((x.get("metadata") or {}).get("chunk_index", 10**9)) * 0  # stable tie helper
            ),
            reverse=True,
        )

        top = scored[:final_top_k]

        # For prompt coherence, sort by document order if enabled
        if settings.RAG_PROMPT_SORT_CHUNKS_BY_INDEX:
            top.sort(key=lambda x: (x.get("metadata") or {}).get("chunk_index", 10**9))

        logger.debug(
            "retrieval_rerank_scores | top=%s",
            [
                {
                    "id": x.get("id"),
                    "score": round(x.get("_rerank_score", 0.0), 4),
                    "distance": x.get("distance"),
                    "chunk_index": (x.get("metadata") or {}).get("chunk_index"),
                    "breakdown": x.get("_score_breakdown"),
                }
                for x in top
            ],
        )

        # Hide internal scoring before returning downstream (optional)
        for item in top:
            item.pop("_score_breakdown", None)
            item.pop("_rerank_score", None)

        return top

    def _score_candidate(
        self,
        question_norm: str,
        question_terms: List[str],
        question_ngrams: List[str],
        candidate: Dict[str, Any],
        total_candidates: int,
    ) -> Dict[str, Any]:
        text = candidate.get("text") or ""
        md = candidate.get("metadata") or {}

        # Include section header / metadata text for lexical matching
        section = str(md.get("section_path") or "")
        ctype = str(md.get("content_type") or "")
        combined = f"{section}\n{text}".strip()
        combined_norm = self._normalize_text(combined)
        candidate_terms = set(self._tokenize_for_matching(combined_norm))

        q_term_set = set(question_terms)

        # 1) lexical overlap (query terms present in candidate)
        overlap_count = len(q_term_set & candidate_terms)
        lexical_overlap = overlap_count / max(1, len(q_term_set))

        # 2) phrase / n-gram hits (helps "test plan", "business case", etc.)
        phrase_hits = 0
        for ng in question_ngrams:
            if ng and ng in combined_norm:
                phrase_hits += 1
        phrase_score = phrase_hits / max(1, len(question_ngrams)) if question_ngrams else 0.0

        # 3) semantic score from vector distance and original rank
        distance = candidate.get("distance")
        if isinstance(distance, (int, float)):
            # Chroma distances: smaller is better. Map to (0,1].
            semantic_from_distance = 1.0 / (1.0 + max(0.0, float(distance)))
        else:
            semantic_from_distance = 0.0

        original_rank = candidate.get("rank")
        if isinstance(original_rank, int) and total_candidates > 0:
            rank_score = (total_candidates - original_rank) / total_candidates
        else:
            rank_score = 0.0

        semantic_score = max(semantic_from_distance, rank_score)

        # 4) short-fragment penalty (very important for your case)
        text_len = len(text.strip())
        short_penalty = 0.0
        if text_len < settings.RAG_RERANK_MIN_CHUNK_CHARS:
            short_penalty = 0.20  # penalize tiny fragments

        # 5) section/header bonus (if query terms appear in section title)
        section_norm = self._normalize_text(section)
        section_terms = set(self._tokenize_for_matching(section_norm))
        section_overlap = len(q_term_set & section_terms) / max(1, len(q_term_set)) if section_terms else 0.0
        header_bonus = 0.05 if ctype in {"header", "section_window"} else 0.0

        # Weighted blend
        score = (
            0.40 * semantic_score +
            0.35 * lexical_overlap +
            0.20 * phrase_score +
            0.10 * section_overlap +
            header_bonus -
            short_penalty
        )

        return {
            "score": score,
            "semantic_score": semantic_score,
            "semantic_from_distance": semantic_from_distance,
            "rank_score": rank_score,
            "lexical_overlap": lexical_overlap,
            "phrase_score": phrase_score,
            "section_overlap": section_overlap,
            "short_penalty": short_penalty,
            "text_len": text_len,
            "distance": distance,
            "rank": original_rank,
        }

    # ---------------------------
    # Neighbor expansion
    # ---------------------------
    def _expand_neighbors(self, doc_id: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not chunks:
            return chunks

        if not settings.RAG_RETRIEVAL_EXPAND_NEIGHBORS:
            return chunks

        radius = max(0, settings.RAG_RETRIEVAL_NEIGHBOR_RADIUS)
        if radius == 0:
            return chunks

        # Pull all chunks for this doc (POC-friendly approach)
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
                    # neighbors don't have original distance/rank from initial query
                    "distance": None,
                    "rank": None,
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

    # ---------------------------
    # Text helpers
    # ---------------------------
    def _normalize_text(self, text: str) -> str:
        text = (text or "").lower()
        text = re.sub(r"[_/\\\-]+", " ", text)   # split joined words like test-plan
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _tokenize_for_matching(self, text: str) -> List[str]:
        norm = self._normalize_text(text)
        tokens = norm.split()

        stopwords = {
            "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
            "by", "is", "are", "be", "as", "at", "from", "that", "this", "it",
            "over", "into", "than", "then", "all", "full", "create", "build",
            "mentioned", "doc", "document",
        }

        out = []
        for t in tokens:
            if len(t) < 2:
                continue
            if t in stopwords:
                continue
            out.append(t)

        # preserve order, remove duplicates
        seen = set()
        ordered_unique = []
        for t in out:
            if t in seen:
                continue
            seen.add(t)
            ordered_unique.append(t)
        return ordered_unique

    def _query_ngrams(self, terms: List[str], n_values=(2, 3)) -> List[str]:
        ngrams = []
        for n in n_values:
            if len(terms) < n:
                continue
            for i in range(len(terms) - n + 1):
                ng = " ".join(terms[i:i+n])
                ngrams.append(ng)
        return ngrams