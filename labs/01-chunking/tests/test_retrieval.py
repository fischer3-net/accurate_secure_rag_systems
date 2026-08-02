"""
Unit tests for Lab 1.2 hybrid retrieval + RRF + re-ranking.

Run from labs/01-chunking:

    pytest tests/test_retrieval.py -v
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import process_directory
from src.ingest import write_jsonl, load_jsonl
from src.retrieval import (
    HybridRetriever,
    BM25Index,
    HashingEmbedder,
    reciprocal_rank_fusion,
    simple_rerank,
    evaluate_retriever,
    load_eval_queries,
    precision_at_k,
    ScoredChunk,
)


DATA_DIR = ROOT / "data"
EVAL_PATH = DATA_DIR / "evaluation_queries.json"


@pytest.fixture(scope="module")
def corpus():
    records = process_directory(DATA_DIR)
    assert len(records) >= 5
    return records


@pytest.fixture(scope="module")
def retriever(corpus):
    return HybridRetriever.from_records(corpus, embedder=HashingEmbedder())


@pytest.fixture(scope="module")
def eval_queries():
    assert EVAL_PATH.exists()
    return load_eval_queries(EVAL_PATH)


# ---------------------------------------------------------------------------
# BM25
# ---------------------------------------------------------------------------

def test_bm25_returns_ranked_results(corpus):
    idx = BM25Index().fit(corpus)
    hits = idx.search("external entity write access data store", top_k=5)
    assert len(hits) > 0
    assert hits[0].score >= hits[-1].score
    assert hits[0].source == "bm25"
    # Should surface SEC-DFD-014 somewhere in top results
    control_ids = {h.control_id for h in hits if h.control_id}
    assert "SEC-DFD-014" in control_ids


def test_bm25_control_id_query(corpus):
    idx = BM25Index().fit(corpus)
    hits = idx.search("SEC-DFD-031", top_k=3)
    assert any(h.control_id == "SEC-DFD-031" for h in hits)


# ---------------------------------------------------------------------------
# RRF
# ---------------------------------------------------------------------------

def test_rrf_merges_lists(corpus):
    idx = BM25Index().fit(corpus)
    list_a = idx.search("trust boundary", top_k=5)
    list_b = idx.search("data flow integrity", top_k=5)
    fused = reciprocal_rank_fusion([list_a, list_b], top_k=5)
    assert len(fused) > 0
    assert fused[0].source == "rrf"
    # Scores should be positive and sorted
    scores = [h.score for h in fused]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# HybridRetriever end-to-end
# ---------------------------------------------------------------------------

def test_hybrid_retrieve_basic(retriever):
    result = retriever.retrieve(
        "Can an external entity write directly to an internal data store?",
        top_k=3,
    )
    assert result.final_hits
    assert result.bm25_hits  # BM25 always on
    control_ids = [h.control_id for h in result.final_hits]
    assert "SEC-DFD-014" in control_ids


def test_hybrid_metadata_filter(retriever):
    result = retriever.retrieve(
        "trust boundary",
        top_k=5,
        asset_type="trust_boundary",
    )
    assert result.filters_applied.get("asset_type") == "trust_boundary"
    for hit in result.final_hits:
        assert hit.record.asset_type == "trust_boundary"


def test_hybrid_bm25_only(retriever):
    result = retriever.retrieve(
        "SEC-DFD-022 data store classification",
        top_k=3,
        use_dense=False,
        use_rerank=False,
    )
    assert result.dense_hits == []
    assert result.bm25_hits
    assert any(h.control_id == "SEC-DFD-022" for h in result.final_hits)


def test_precision_at_k_helper():
    # Synthetic
    from src.metadata import ChunkRecord

    relevant = ["SEC-DFD-014"]
    hits = [
        ScoredChunk(
            record=ChunkRecord(
                doc_type="security_baseline",
                section="x",
                source_uri="x",
                text="…",
                control_id="SEC-DFD-014",
            ),
            score=1.0,
            rank=1,
        ),
        ScoredChunk(
            record=ChunkRecord(
                doc_type="security_baseline",
                section="y",
                source_uri="y",
                text="…",
                control_id="SEC-DFD-001",
            ),
            score=0.5,
            rank=2,
        ),
    ]
    assert precision_at_k(hits, relevant, k=1) == 1.0
    assert precision_at_k(hits, relevant, k=2) == 0.5


def test_evaluate_retriever_runs(retriever, eval_queries):
    metrics = evaluate_retriever(
        retriever,
        eval_queries,
        k=3,
        use_dense=True,
        use_bm25=True,
        use_rerank=True,
    )
    assert "mean_precision_at_3" in metrics
    assert "mean_hit_rate_at_3" in metrics
    assert metrics["n_queries"] == len(eval_queries)
    assert 0.0 <= metrics["mean_precision_at_3"] <= 1.0
    assert 0.0 <= metrics["mean_hit_rate_at_3"] <= 1.0
    # Hit-rate is the primary success signal for control lookup
    assert metrics["mean_hit_rate_at_3"] >= 0.5


def test_jsonl_roundtrip_with_retrieval(corpus, tmp_path):
    path = tmp_path / "corpus.jsonl"
    write_jsonl(corpus, path)
    retriever = HybridRetriever.from_jsonl(path, embedder=HashingEmbedder())
    result = retriever.retrieve("process isolation different trust levels", top_k=3)
    assert result.final_hits
    assert any(h.control_id == "SEC-DFD-045" for h in result.final_hits)
