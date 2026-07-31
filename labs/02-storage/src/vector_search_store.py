"""
Vertex AI Vector Search *style* pure semantic store (offline simulation).

Simulates the Matching Engine pattern:

- Documents are indexed primarily by embedding.
- Metadata filters (restricts) are applied either pre- or post-retrieval
  in application code (or via restricted tokens in a real index).

Again, the in-memory implementation lets the lab run offline while
preserving the interface you would use with the Vertex AI SDK.
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


class VectorSearchStore(VectorStore):
    """In-memory pure-semantic store that simulates Vertex AI Vector Search."""

    name = "vector_search"

    def __init__(self, dim: int = 256, candidate_multiplier: int = 4):
        self.dim = dim
        # Fetch more candidates then filter – mirrors “retrieve then restrict”
        self.candidate_multiplier = candidate_multiplier
        self._rows: list[dict[str, Any]] = []

    def upsert(self, records: Sequence[Any]) -> int:
        self._rows.clear()
        for r in records:
            if hasattr(r, "to_dict"):
                d = r.to_dict()
            elif hasattr(r, "model_dump"):
                d = r.model_dump()
            else:
                d = dict(r)
            d = dict(d)
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

        # 1. Pure semantic ranking over the full corpus
        scored = [
            (_cosine(q_vec, row["_embedding"]), row) for row in self._rows
        ]
        scored.sort(key=lambda x: x[0], reverse=True)

        # 2. Application-side metadata restrict (Vector Search style)
        def _match(val: Any, allowed: Optional[str | Sequence[str]]) -> bool:
            if allowed is None:
                return True
            if isinstance(allowed, str):
                return val == allowed
            return val in allowed

        candidate_pool = max(top_k * self.candidate_multiplier, top_k)
        hits: list[StoreHit] = []
        for score, row in scored[:candidate_pool]:
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
            hits.append(
                StoreHit(
                    chunk_id=row.get("chunk_id", ""),
                    text=row.get("text", ""),
                    score=float(score),
                    rank=len(hits) + 1,
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
            if len(hits) >= top_k:
                break

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
