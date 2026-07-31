"""
AlloyDB / Cloud SQL + pgvector *style* hybrid store (offline simulation).

This in-memory implementation supports the same hybrid pattern you would
express in SQL:

    SELECT * FROM chunks
    WHERE risk_tier = 'critical'
      AND asset_type = 'trust_boundary'
    ORDER BY embedding <=> $query_embedding
    LIMIT k;

For the workshop it uses the Week 1 HashingEmbedder + linear scan so it
runs without a database.  The public methods mirror what a real
psycopg / asyncpg + pgvector client would expose, making a later swap
straightforward.
"""

from __future__ import annotations

import math
import time
from typing import Any, Optional, Sequence

from .store_base import StoreHit, StoreSearchResult, VectorStore


def _tokenize(text: str) -> list[str]:
    import re
    return [t.lower() for t in re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text, re.I)]


def _hash_embed(text: str, dim: int = 256) -> list[float]:
    vec = [0.0] * dim
    for tok in _tokenize(text):
        h = hash(tok) % dim
        sign = 1.0 if hash(tok + "s") % 2 == 0 else -1.0
        vec[h] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class PgVectorStore(VectorStore):
    """In-memory hybrid store that simulates AlloyDB + pgvector behaviour."""

    name = "pgvector"

    def __init__(self, dim: int = 256):
        self.dim = dim
        self._rows: list[dict[str, Any]] = []

    def upsert(self, records: Sequence[Any]) -> int:
        self._rows.clear()
        for r in records:
            # Accept ChunkRecord or plain dict
            if hasattr(r, "to_dict"):
                d = r.to_dict()
            elif hasattr(r, "model_dump"):
                d = r.model_dump()
            else:
                d = dict(r)
            d = dict(d)  # copy
            d["_embedding"] = _hash_embed(d.get("text", ""), self.dim)
            self._rows.append(d)
        return len(self._rows)

    def count(self) -> int:
        return len(self._rows)

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        asset_type: Optional[str | Sequence[str]] = None,
        risk_tier: Optional[str | Sequence[str]] = None,
        sdlc_phase: Optional[str | Sequence[str]] = None,
        doc_type: Optional[str | Sequence[str]] = None,
        control_id: Optional[str] = None,
    ) -> StoreSearchResult:
        t0 = time.perf_counter()
        q_vec = _hash_embed(query, self.dim)

        def _match(val: Any, allowed: Optional[str | Sequence[str]]) -> bool:
            if allowed is None:
                return True
            if isinstance(allowed, str):
                return val == allowed
            return val in allowed

        candidates = []
        for row in self._rows:
            if not _match(row.get("asset_type"), asset_type):
                continue
            if not _match(row.get("risk_tier"), risk_tier):
                continue
            if not _match(row.get("sdlc_phase"), sdlc_phase):
                continue
            if not _match(row.get("doc_type"), doc_type):
                continue
            if control_id is not None and row.get("control_id") != control_id:
                continue
            score = _cosine(q_vec, row["_embedding"])
            candidates.append((score, row))

        candidates.sort(key=lambda x: x[0], reverse=True)
        hits: list[StoreHit] = []
        for rank, (score, row) in enumerate(candidates[:top_k], start=1):
            hits.append(
                StoreHit(
                    chunk_id=row.get("chunk_id", ""),
                    text=row.get("text", ""),
                    score=float(score),
                    rank=rank,
                    control_id=row.get("control_id"),
                    metadata={
                        k: row.get(k)
                        for k in (
                            "doc_type",
                            "section",
                            "asset_type",
                            "risk_tier",
                            "sdlc_phase",
                            "chunk_type",
                        )
                    },
                )
            )

        latency = (time.perf_counter() - t0) * 1000
        return StoreSearchResult(
            query=query,
            hits=hits,
            backend=self.name,
            latency_ms=latency,
            filters={
                k: v
                for k, v in {
                    "asset_type": asset_type,
                    "risk_tier": risk_tier,
                    "sdlc_phase": sdlc_phase,
                    "doc_type": doc_type,
                    "control_id": control_id,
                }.items()
                if v is not None
            },
        )
