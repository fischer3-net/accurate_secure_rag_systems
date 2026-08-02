"""
Hybrid retrieval + Reciprocal Rank Fusion + re-ranking for Lab 1.2.

Design goals
------------
* Work offline for BM25 + RRF (no GCP required for core path).
* Provide a clean interface for Vertex AI Embeddings when credentials exist.
* Support metadata pre-filtering (asset_type, risk_tier, control_id, …).
* Expose a simple, measurable precision@k evaluation harness.
* Keep the API small enough that the same retriever can be reused in
  Lab 3 skills and the Capstone.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from .metadata import ChunkRecord
from .ingest import load_jsonl


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ScoredChunk:
    """A chunk returned by a retriever together with its score and rank."""
    record: ChunkRecord
    score: float
    rank: int = 0
    source: str = ""          # "bm25" | "dense" | "rrf" | "rerank"
    explanation: dict[str, Any] = field(default_factory=dict)

    @property
    def chunk_id(self) -> str:
        return self.record.chunk_id

    @property
    def text(self) -> str:
        return self.record.text

    @property
    def control_id(self) -> Optional[str]:
        return self.record.control_id


@dataclass
class RetrievalResult:
    """Full result of a hybrid query, useful for debugging and evaluation."""
    query: str
    bm25_hits: list[ScoredChunk] = field(default_factory=list)
    dense_hits: list[ScoredChunk] = field(default_factory=list)
    fused_hits: list[ScoredChunk] = field(default_factory=list)
    final_hits: list[ScoredChunk] = field(default_factory=list)
    filters_applied: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.IGNORECASE)


def tokenize(text: str) -> list[str]:
    """Simple alphanumeric tokenizer that preserves hyphenated control IDs."""
    return [t.lower() for t in _TOKEN_RE.findall(text)]


# ---------------------------------------------------------------------------
# BM25 (pure Python – no external dependency required for the core path)
# ---------------------------------------------------------------------------

class BM25Index:
    """
    Classic BM25 (Robertson / Zaragoza).

    Implemented in pure Python so the lab runs without extra packages.
    For production you may swap in `rank_bm25` or a real search engine.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents: list[ChunkRecord] = []
        self.doc_tokens: list[list[str]] = []
        self.doc_len: list[int] = []
        self.avgdl: float = 0.0
        self.df: dict[str, int] = defaultdict(int)
        self.idf: dict[str, float] = {}
        self.N: int = 0

    def fit(self, records: Sequence[ChunkRecord]) -> "BM25Index":
        self.documents = list(records)
        self.doc_tokens = [tokenize(r.text) for r in records]
        self.doc_len = [len(toks) for toks in self.doc_tokens]
        self.N = len(records)
        self.avgdl = sum(self.doc_len) / self.N if self.N else 0.0

        df: dict[str, int] = defaultdict(int)
        for toks in self.doc_tokens:
            for t in set(toks):
                df[t] += 1
        self.df = df
        self.idf = {
            t: math.log(1 + (self.N - freq + 0.5) / (freq + 0.5))
            for t, freq in df.items()
        }
        return self

    def search(self, query: str, top_k: int = 10) -> list[ScoredChunk]:
        q_tokens = tokenize(query)
        if not q_tokens or not self.documents:
            return []

        scores = [0.0] * self.N
        for i, toks in enumerate(self.doc_tokens):
            if not toks:
                continue
            tf: dict[str, int] = defaultdict(int)
            for t in toks:
                tf[t] += 1
            dl = self.doc_len[i]
            for qt in q_tokens:
                if qt not in tf:
                    continue
                idf = self.idf.get(qt, 0.0)
                freq = tf[qt]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
                scores[i] += idf * (freq * (self.k1 + 1)) / denom

        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results: list[ScoredChunk] = []
        for rank, (idx, score) in enumerate(ranked[:top_k], start=1):
            if score <= 0:
                break
            results.append(
                ScoredChunk(
                    record=self.documents[idx],
                    score=float(score),
                    rank=rank,
                    source="bm25",
                )
            )
        return results


# ---------------------------------------------------------------------------
# Dense embedding interface
# ---------------------------------------------------------------------------

class DenseEmbedder:
    """
    Abstract dense embedder.

    Two concrete implementations are provided:
    - HashingEmbedder  – offline, deterministic, no dependencies (for tests
                         and environments without Vertex credentials)
    - VertexEmbedder   – real Vertex AI text-embedding-004 (or later)
    """

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        raise NotImplementedError

    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class HashingEmbedder(DenseEmbedder):
    """
    Lightweight feature hashing embedder.

    Produces sparse-ish fixed-size vectors from token hashes.
    Not a substitute for a real embedding model, but sufficient to exercise
    the dense + RRF path offline and in unit tests.
    """

    def __init__(self, dim: int = 256, seed: int = 42):
        self.dim = dim
        self.seed = seed

    def _vectorize(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in tokenize(text):
            # Simple deterministic hash
            h = hash((tok, self.seed)) % self.dim
            sign = 1.0 if (hash((tok, self.seed, "s")) % 2 == 0) else -1.0
            vec[h] += sign
        # L2 normalise
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._vectorize(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._vectorize(text)


class VertexEmbedder(DenseEmbedder):
    """
    Vertex AI text-embedding-004 (or the current equivalent).

    Requires Application Default Credentials and the Vertex AI API.
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: str = "us-central1",
        model: str = "text-embedding-004",
    ):
        from google.cloud import aiplatform
        import os

        project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            raise ValueError(
                "project_id required (or set GOOGLE_CLOUD_PROJECT)"
            )
        aiplatform.init(project=project_id, location=location)
        self.model = model
        self._client = None  # lazy

    def _get_client(self):
        if self._client is None:
            from vertexai.language_models import TextEmbeddingModel
            self._client = TextEmbeddingModel.from_pretrained(self.model)
        return self._client

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._get_client()
        # Vertex accepts batches; keep them modest
        embeddings = []
        batch_size = 32
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            result = model.get_embeddings(batch)
            embeddings.extend([e.values for e in result])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


class DenseIndex:
    """In-memory dense index over ChunkRecords."""

    def __init__(self, embedder: DenseEmbedder):
        self.embedder = embedder
        self.documents: list[ChunkRecord] = []
        self.vectors: list[list[float]] = []

    def fit(self, records: Sequence[ChunkRecord]) -> "DenseIndex":
        self.documents = list(records)
        texts = [r.text for r in records]
        self.vectors = self.embedder.embed_documents(texts)
        return self

    def search(self, query: str, top_k: int = 10) -> list[ScoredChunk]:
        if not self.documents:
            return []
        q_vec = self.embedder.embed_query(query)
        scored = [
            (i, cosine_similarity(q_vec, v))
            for i, v in enumerate(self.vectors)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        results: list[ScoredChunk] = []
        for rank, (idx, score) in enumerate(scored[:top_k], start=1):
            if score <= 0:
                break
            results.append(
                ScoredChunk(
                    record=self.documents[idx],
                    score=float(score),
                    rank=rank,
                    source="dense",
                )
            )
        return results


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion
# ---------------------------------------------------------------------------

def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[ScoredChunk]],
    *,
    k: int = 60,
    top_k: int = 10,
) -> list[ScoredChunk]:
    """
    Classic RRF:

        score(d) = Σ  1 / (k + rank_r(d))

    where rank_r is 1-based rank in each ranked list.
    """
    scores: dict[str, float] = defaultdict(float)
    best_record: dict[str, ChunkRecord] = {}
    sources: dict[str, list[str]] = defaultdict(list)

    for ranked in ranked_lists:
        for item in ranked:
            cid = item.chunk_id
            scores[cid] += 1.0 / (k + item.rank)
            best_record[cid] = item.record
            sources[cid].append(item.source)

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    results: list[ScoredChunk] = []
    for rank, (cid, score) in enumerate(fused[:top_k], start=1):
        results.append(
            ScoredChunk(
                record=best_record[cid],
                score=float(score),
                rank=rank,
                source="rrf",
                explanation={"contributing_sources": sources[cid]},
            )
        )
    return results


# ---------------------------------------------------------------------------
# Lightweight re-ranker (score combination + optional cross-signal boost)
# ---------------------------------------------------------------------------

def simple_rerank(
    query: str,
    candidates: Sequence[ScoredChunk],
    *,
    top_k: int = 5,
    control_id_boost: float = 0.15,
    exact_phrase_boost: float = 0.10,
) -> list[ScoredChunk]:
    """
    Lightweight, deterministic re-ranker.

    Boosts candidates that:
    - contain an exact control ID present in the query, or
    - contain a long exact phrase overlap with the query.

    This is intentionally simple and auditable — suitable for a security
    lab.  In production you would typically call Vertex AI Ranking API or
    a cross-encoder here.
    """
    q_lower = query.lower()
    q_tokens = set(tokenize(query))
    control_in_query = set(re.findall(r"SEC-[A-Z]+-\d+", query.upper()))

    rescored: list[ScoredChunk] = []
    for c in candidates:
        score = c.score
        text_lower = c.text.lower()

        # Control-ID exact match boost
        if c.control_id and c.control_id in control_in_query:
            score += control_id_boost

        # Phrase / token overlap boost
        overlap = len(q_tokens & set(tokenize(c.text))) / max(len(q_tokens), 1)
        score += exact_phrase_boost * overlap

        # Prefer children / standalone over pure parents for precision
        if c.record.chunk_type == "parent":
            score *= 0.92

        rescored.append(
            ScoredChunk(
                record=c.record,
                score=score,
                rank=0,
                source="rerank",
                explanation={
                    "original_score": c.score,
                    "original_source": c.source,
                },
            )
        )

    rescored.sort(key=lambda x: x.score, reverse=True)
    for i, item in enumerate(rescored[:top_k], start=1):
        item.rank = i
    return rescored[:top_k]


# ---------------------------------------------------------------------------
# Metadata filtering
# ---------------------------------------------------------------------------

def apply_metadata_filters(
    records: Sequence[ChunkRecord],
    *,
    doc_type: Optional[str] = None,
    asset_type: Optional[str | Sequence[str]] = None,
    risk_tier: Optional[str | Sequence[str]] = None,
    sdlc_phase: Optional[str | Sequence[str]] = None,
    control_id: Optional[str] = None,
    chunk_type: Optional[str | Sequence[str]] = None,
) -> list[ChunkRecord]:
    """Filter a corpus by any combination of metadata fields."""

    def _match(value: Any, allowed: Optional[str | Sequence[str]]) -> bool:
        if allowed is None:
            return True
        if isinstance(allowed, str):
            return value == allowed
        return value in allowed

    out: list[ChunkRecord] = []
    for r in records:
        if not _match(r.doc_type, doc_type):
            continue
        if not _match(r.asset_type, asset_type):
            continue
        if not _match(r.risk_tier, risk_tier):
            continue
        if not _match(r.sdlc_phase, sdlc_phase):
            continue
        if control_id is not None and r.control_id != control_id:
            continue
        if not _match(r.chunk_type, chunk_type):
            continue
        out.append(r)
    return out


# ---------------------------------------------------------------------------
# High-level HybridRetriever
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    End-to-end hybrid retriever used by Lab 1.2 and later modules.

    Typical usage
    -------------
    >>> retriever = HybridRetriever.from_jsonl("output/rag_chunks.jsonl")
    >>> result = retriever.retrieve(
    ...     "Can external entities write directly to data stores?",
    ...     top_k=5,
    ...     asset_type="external_entity",
    ... )
    >>> for hit in result.final_hits:
    ...     print(hit.rank, hit.control_id, hit.score)
    """

    def __init__(
        self,
        records: Sequence[ChunkRecord],
        *,
        embedder: Optional[DenseEmbedder] = None,
        rrf_k: int = 60,
    ):
        self.records = list(records)
        self.rrf_k = rrf_k

        # Always build BM25
        self.bm25 = BM25Index().fit(self.records)

        # Dense index (HashingEmbedder by default so the lab runs offline)
        self.embedder = embedder or HashingEmbedder()
        self.dense = DenseIndex(self.embedder).fit(self.records)

    @classmethod
    def from_jsonl(
        cls,
        path: Path | str,
        *,
        embedder: Optional[DenseEmbedder] = None,
        rrf_k: int = 60,
    ) -> "HybridRetriever":
        records = load_jsonl(path)
        return cls(records, embedder=embedder, rrf_k=rrf_k)

    @classmethod
    def from_records(
        cls,
        records: Sequence[ChunkRecord],
        *,
        embedder: Optional[DenseEmbedder] = None,
        rrf_k: int = 60,
    ) -> "HybridRetriever":
        return cls(records, embedder=embedder, rrf_k=rrf_k)

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 20,
        use_dense: bool = True,
        use_bm25: bool = True,
        use_rerank: bool = True,
        # metadata filters
        doc_type: Optional[str] = None,
        asset_type: Optional[str | Sequence[str]] = None,
        risk_tier: Optional[str | Sequence[str]] = None,
        sdlc_phase: Optional[str | Sequence[str]] = None,
        control_id: Optional[str] = None,
        chunk_type: Optional[str | Sequence[str]] = None,
    ) -> RetrievalResult:
        """
        Run the full hybrid pipeline and return a rich RetrievalResult.

        Parameters
        ----------
        candidate_k :
            How many hits to request from each base retriever before fusion.
        top_k :
            Final number of results after fusion / re-ranking.
        """
        filters = {
            k: v
            for k, v in {
                "doc_type": doc_type,
                "asset_type": asset_type,
                "risk_tier": risk_tier,
                "sdlc_phase": sdlc_phase,
                "control_id": control_id,
                "chunk_type": chunk_type,
            }.items()
            if v is not None
        }

        # Optional pre-filter of the corpus
        working = self.records
        if filters:
            working = apply_metadata_filters(self.records, **filters)
            # Rebuild lightweight indexes over the filtered set for correctness
            bm25 = BM25Index().fit(working)
            dense = DenseIndex(self.embedder).fit(working)
        else:
            bm25 = self.bm25
            dense = self.dense

        bm25_hits: list[ScoredChunk] = []
        dense_hits: list[ScoredChunk] = []

        if use_bm25 and working:
            bm25_hits = bm25.search(query, top_k=candidate_k)
        if use_dense and working:
            dense_hits = dense.search(query, top_k=candidate_k)

        ranked_lists = []
        if bm25_hits:
            ranked_lists.append(bm25_hits)
        if dense_hits:
            ranked_lists.append(dense_hits)

        if not ranked_lists:
            return RetrievalResult(
                query=query,
                filters_applied=filters,
            )

        fused = reciprocal_rank_fusion(
            ranked_lists, k=self.rrf_k, top_k=candidate_k
        )

        if use_rerank:
            final = simple_rerank(query, fused, top_k=top_k)
        else:
            final = fused[:top_k]
            for i, item in enumerate(final, start=1):
                item.rank = i

        return RetrievalResult(
            query=query,
            bm25_hits=bm25_hits,
            dense_hits=dense_hits,
            fused_hits=fused,
            final_hits=final,
            filters_applied=filters,
        )


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

@dataclass
class EvalQuery:
    query_id: str
    query: str
    relevant_control_ids: list[str]
    relevant_asset_types: list[str] = field(default_factory=list)
    notes: str = ""


def load_eval_queries(path: Path | str) -> list[EvalQuery]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvalQuery(**item) for item in raw]


def precision_at_k(
    hits: Sequence[ScoredChunk],
    relevant_control_ids: Sequence[str],
    k: int = 3,
) -> float:
    """
    Precision@k measured against control_id ground truth.

    A hit is relevant if its control_id is in the expected set.
    Chunks without a control_id are treated as non-relevant for this metric
    (they may still be useful context, but the lab focuses on control lookup).
    """
    if not relevant_control_ids:
        # Queries without a specific control_id (e.g. broad gate questions)
        # are scored leniently: any non-empty hit list scores 1.0
        return 1.0 if hits[:k] else 0.0

    relevant = set(relevant_control_ids)
    top = hits[:k]
    if not top:
        return 0.0
    hits_relevant = sum(1 for h in top if h.control_id in relevant)
    return hits_relevant / len(top)


def hit_rate_at_k(
    hits: Sequence[ScoredChunk],
    relevant_control_ids: Sequence[str],
    k: int = 3,
) -> float:
    """
    Hit-rate@k (also called Recall@k when there is a single relevant item):
    1.0 if at least one relevant control_id appears in the top-k, else 0.0.

    This is often the more meaningful metric for compliance lookup tasks
    where the user needs *the* correct control, not a high precision ratio.
    """
    if not relevant_control_ids:
        return 1.0 if hits[:k] else 0.0
    relevant = set(relevant_control_ids)
    return 1.0 if any(h.control_id in relevant for h in hits[:k]) else 0.0


def evaluate_retriever(
    retriever: HybridRetriever,
    queries: Sequence[EvalQuery],
    *,
    k: int = 3,
    use_dense: bool = True,
    use_bm25: bool = True,
    use_rerank: bool = True,
) -> dict[str, Any]:
    """
    Run a full evaluation suite and return aggregate metrics + per-query detail.

    Reports both mean precision@k and mean hit-rate@k.  Hit-rate is the
    primary success metric for this lab (\"did we surface the right control?\").
    """
    per_query = []
    p_scores = []
    hit_scores = []

    for q in queries:
        result = retriever.retrieve(
            q.query,
            top_k=k,
            use_dense=use_dense,
            use_bm25=use_bm25,
            use_rerank=use_rerank,
        )
        p = precision_at_k(result.final_hits, q.relevant_control_ids, k=k)
        h = hit_rate_at_k(result.final_hits, q.relevant_control_ids, k=k)
        p_scores.append(p)
        hit_scores.append(h)
        per_query.append(
            {
                "query_id": q.query_id,
                "query": q.query,
                "precision_at_k": p,
                "hit_rate_at_k": h,
                "retrieved_control_ids": [
                    h_.control_id for h_ in result.final_hits
                ],
                "expected_control_ids": q.relevant_control_ids,
            }
        )

    n = len(queries) or 1
    return {
        f"mean_precision_at_{k}": sum(p_scores) / n,
        f"mean_hit_rate_at_{k}": sum(hit_scores) / n,
        "n_queries": len(queries),
        "per_query": per_query,
    }
