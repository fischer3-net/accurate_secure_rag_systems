"""Tests for Lab 2.1 storage backends and benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.pgvector_store import PgVectorStore
from src.vector_search_store import VectorSearchStore
from src.benchmark import run_benchmark


def test_pgvector_upsert_and_search(week1_corpus):
    store = PgVectorStore()
    n = store.upsert(week1_corpus)
    assert n == len(week1_corpus)
    result = store.search("external entity write access", top_k=3)
    assert result.backend == "pgvector"
    assert len(result.hits) > 0
    assert result.latency_ms >= 0


def test_pgvector_metadata_filter(week1_corpus):
    store = PgVectorStore()
    store.upsert(week1_corpus)
    result = store.search("boundary", top_k=5, asset_type="trust_boundary")
    for h in result.hits:
        assert h.metadata.get("asset_type") == "trust_boundary"


def test_vector_search_upsert_and_search(week1_corpus):
    store = VectorSearchStore()
    store.upsert(week1_corpus)
    result = store.search("data store classification", top_k=3)
    assert result.backend == "vector_search"
    assert len(result.hits) > 0


def test_benchmark_runs(week1_corpus, week1_queries):
    pg = PgVectorStore()
    pg.upsert(week1_corpus)
    vs = VectorSearchStore()
    vs.upsert(week1_corpus)
    report = run_benchmark(
        {"pgvector": pg, "vector_search": vs},
        week1_queries,
        k=3,
    )
    assert len(report.backends) == 2
    for b in report.backends:
        assert 0.0 <= b.mean_hit_rate_at_k <= 1.0
        assert b.n_queries == len(week1_queries)
    print(report.summary())
