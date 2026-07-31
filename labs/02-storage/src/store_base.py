"""
Common storage interface for Lab 2.1.

Both the AlloyDB-style (hybrid) and Vector-Search-style backends implement
this interface so the benchmark harness and later Capstone skills can swap
stores without changing call sites.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


@dataclass
class StoreHit:
    chunk_id: str
    text: str
    score: float
    rank: int
    metadata: dict[str, Any] = field(default_factory=dict)
    control_id: Optional[str] = None


@dataclass
class StoreSearchResult:
    query: str
    hits: list[StoreHit]
    backend: str
    latency_ms: float = 0.0
    filters: dict[str, Any] = field(default_factory=dict)


class VectorStore(ABC):
    """Minimal contract every Lab 2.1 backend must satisfy."""

    name: str = "base"

    @abstractmethod
    def upsert(self, records: Sequence[Any]) -> int:
        """Index or re-index ChunkRecord-like objects. Returns count written."""

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        # common metadata filters
        asset_type: Optional[str | Sequence[str]] = None,
        risk_tier: Optional[str | Sequence[str]] = None,
        sdlc_phase: Optional[str | Sequence[str]] = None,
        doc_type: Optional[str | Sequence[str]] = None,
        control_id: Optional[str] = None,
    ) -> StoreSearchResult:
        """Return ranked hits. Filters are best-effort per backend."""

    def count(self) -> int:
        return 0
