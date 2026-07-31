"""
Shared benchmark harness for Lab 2.1.

Compares any number of VectorStore backends on the same query set and
reports hit-rate@k, precision@k, and simple latency statistics.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Sequence

from .store_base import StoreSearchResult, VectorStore


@dataclass
class EvalQuery:
    query_id: str
    query: str
    relevant_control_ids: list[str] = field(default_factory=list)
    relevant_asset_types: list[str] = field(default_factory=list)
    notes: str = ""


def load_eval_queries(path: Path | str) -> list[EvalQuery]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [EvalQuery(**item) for item in raw]


def hit_rate_at_k(hits_control_ids: Sequence[Optional[str]], relevant: Sequence[str], k: int = 3) -> float:
    if not relevant:
        return 1.0 if hits_control_ids[:k] else 0.0
    rel = set(relevant)
    return 1.0 if any(c in rel for c in hits_control_ids[:k]) else 0.0


def precision_at_k(hits_control_ids: Sequence[Optional[str]], relevant: Sequence[str], k: int = 3) -> float:
    if not relevant:
        return 1.0 if hits_control_ids[:k] else 0.0
    rel = set(relevant)
    top = hits_control_ids[:k]
    if not top:
        return 0.0
    return sum(1 for c in top if c in rel) / len(top)


@dataclass
class BackendMetrics:
    backend: str
    mean_hit_rate_at_k: float
    mean_precision_at_k: float
    mean_latency_ms: float
    p95_latency_ms: float
    n_queries: int
    per_query: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class BenchmarkReport:
    k: int
    backends: list[BackendMetrics]

    def summary(self) -> str:
        lines = [f"Benchmark  k={self.k}", "-" * 56]
        lines.append(f"{'Backend':20s}  {'Hit@k':>6}  {'P@k':>6}  {'mean ms':>8}  {'p95 ms':>8}")
        for b in self.backends:
            lines.append(
                f"{b.backend:20s}  {b.mean_hit_rate_at_k:6.3f}  {b.mean_precision_at_k:6.3f}  "
                f"{b.mean_latency_ms:8.2f}  {b.p95_latency_ms:8.2f}"
            )
        return "\n".join(lines)


def run_benchmark(
    stores: dict[str, VectorStore],
    queries: Sequence[EvalQuery],
    *,
    k: int = 3,
    # optional global filters applied to every query
    asset_type: Optional[str] = None,
    risk_tier: Optional[str] = None,
) -> BenchmarkReport:
    backend_metrics: list[BackendMetrics] = []

    for name, store in stores.items():
        hit_scores: list[float] = []
        prec_scores: list[float] = []
        latencies: list[float] = []
        per_query: list[dict[str, Any]] = []

        for q in queries:
            result: StoreSearchResult = store.search(
                q.query,
                top_k=k,
                asset_type=asset_type,
                risk_tier=risk_tier,
            )
            cids = [h.control_id for h in result.hits]
            h = hit_rate_at_k(cids, q.relevant_control_ids, k=k)
            p = precision_at_k(cids, q.relevant_control_ids, k=k)
            hit_scores.append(h)
            prec_scores.append(p)
            latencies.append(result.latency_ms)
            per_query.append(
                {
                    "query_id": q.query_id,
                    "hit_rate": h,
                    "precision": p,
                    "latency_ms": result.latency_ms,
                    "retrieved": cids,
                    "expected": q.relevant_control_ids,
                }
            )

        n = len(queries) or 1
        sorted_lat = sorted(latencies)
        p95 = sorted_lat[int(0.95 * (len(sorted_lat) - 1))] if sorted_lat else 0.0
        backend_metrics.append(
            BackendMetrics(
                backend=name,
                mean_hit_rate_at_k=sum(hit_scores) / n,
                mean_precision_at_k=sum(prec_scores) / n,
                mean_latency_ms=statistics.mean(latencies) if latencies else 0.0,
                p95_latency_ms=p95,
                n_queries=len(queries),
                per_query=per_query,
            )
        )

    return BenchmarkReport(k=k, backends=backend_metrics)
