"""Shared fixtures for Lab 2 tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CORPUS_JSONL = ROOT / "data" / "rag_chunks.jsonl"
QUERIES_JSON = (
    Path(__file__).resolve().parents[2] / "01-chunking" / "data" / "evaluation_queries.json"
)


@pytest.fixture(scope="session")
def week1_corpus():
    """Load pre-exported Week 1 chunks as plain dicts."""
    if not CORPUS_JSONL.exists():
        pytest.skip(f"Missing {CORPUS_JSONL} – run Lab 1.1 export first")
    records = []
    for line in CORPUS_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    assert len(records) >= 5
    return records


@pytest.fixture(scope="session")
def week1_queries():
    from src.benchmark import load_eval_queries
    if not QUERIES_JSON.exists():
        pytest.skip(f"Missing {QUERIES_JSON}")
    return load_eval_queries(QUERIES_JSON)
