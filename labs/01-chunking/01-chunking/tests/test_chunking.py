"""
Unit tests for Lab 1.1 chunking + metadata enrichment.

Run from the labs/01-chunking directory:

    pytest tests/ -v

These tests intentionally stay offline (no GCP calls) so they can run
in CI and on student laptops without credentials.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the src package importable when running from labs/01-chunking
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.chunking import process_document, process_directory, split_markdown_file
from src.metadata import (
    ChunkRecord,
    ChunkType,
    extract_control_id,
    infer_asset_type,
    infer_risk_tier,
    infer_sdlc_phase,
    validate_records,
)
from src.ingest import write_jsonl, load_jsonl


DATA_DIR = ROOT / "data"
HANDBOOK = DATA_DIR / "sdlc_handbook.md"
BASELINE = DATA_DIR / "security_baseline.md"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def handbook_records() -> list[ChunkRecord]:
    assert HANDBOOK.exists(), f"Missing sample document: {HANDBOOK}"
    return process_document(HANDBOOK)


@pytest.fixture(scope="module")
def baseline_records() -> list[ChunkRecord]:
    assert BASELINE.exists(), f"Missing sample document: {BASELINE}"
    return process_document(BASELINE)


@pytest.fixture(scope="module")
def full_corpus() -> list[ChunkRecord]:
    return process_directory(DATA_DIR)


# ---------------------------------------------------------------------------
# Metadata inference
# ---------------------------------------------------------------------------

def test_extract_control_id():
    assert extract_control_id("See SEC-DFD-014 for details") == "SEC-DFD-014"
    assert extract_control_id("## SEC-DFD-001 – Trust Boundary") == "SEC-DFD-001"
    assert extract_control_id("No control here") is None


def test_infer_asset_type():
    assert infer_asset_type("Every trust boundary must be documented") == "trust_boundary"
    assert infer_asset_type("External entities shall not have direct write access") == "external_entity"
    assert infer_asset_type("Classify all data stores by sensitivity") == "data_store"
    assert infer_asset_type("Data flows that cross boundaries need integrity") == "data_flow"
    assert infer_asset_type("A generic paragraph about software") == "general"


def test_infer_risk_tier():
    assert infer_risk_tier("**Risk Tier:** Critical") == "critical"
    assert infer_risk_tier("Risk Tier: High") == "high"
    assert infer_risk_tier("This is a medium severity item") == "medium"
    assert infer_risk_tier("No risk language present") == "unspecified"


def test_infer_sdlc_phase():
    assert infer_sdlc_phase("**SDLC Phase:** Design") == "design"
    assert infer_sdlc_phase("Required during the requirements phase") == "requirements"
    assert infer_sdlc_phase("Must be re-validated in verification") == "verification"
    assert infer_sdlc_phase("A neutral statement") == "general"


# ---------------------------------------------------------------------------
# Splitting behaviour
# ---------------------------------------------------------------------------

def test_split_respects_headings():
    docs = split_markdown_file(HANDBOOK)
    assert len(docs) >= 5, "Expected multiple heading-based chunks"

    # Every document should carry at least an h1 or h2
    for d in docs:
        assert any(k in d.metadata for k in ("h1", "h2", "h3")), (
            f"Document missing heading metadata: {d.metadata}"
        )


def test_no_empty_text(handbook_records, baseline_records):
    for r in handbook_records + baseline_records:
        assert r.text.strip(), f"Empty text in chunk {r.chunk_id}"


def test_required_fields_present(full_corpus):
    required = {
        "chunk_id", "doc_type", "section", "asset_type",
        "risk_tier", "sdlc_phase", "source_uri", "chunk_type", "text",
    }
    for r in full_corpus:
        data = r.to_dict()
        missing = required - set(data.keys())
        assert not missing, f"Missing fields {missing} in {r.chunk_id}"
        for f in required:
            assert data[f] is not None and data[f] != "", (
                f"Field {f} is empty in {r.chunk_id}"
            )


def test_doc_type_assignment(handbook_records, baseline_records):
    for r in handbook_records:
        assert r.doc_type == "sdlc_handbook"
    for r in baseline_records:
        assert r.doc_type == "security_baseline"


def test_control_ids_extracted(baseline_records):
    control_ids = {r.control_id for r in baseline_records if r.control_id}
    # Sample baseline contains at least these
    expected = {"SEC-DFD-001", "SEC-DFD-014", "SEC-DFD-022", "SEC-DFD-031", "SEC-DFD-045"}
    assert expected.issubset(control_ids), (
        f"Missing expected control IDs. Found: {control_ids}"
    )


def test_parent_child_linkage(full_corpus):
    """If any child exists, its parent_id must resolve."""
    id_map = {r.chunk_id: r for r in full_corpus}
    children = [r for r in full_corpus if r.chunk_type == ChunkType.CHILD.value]

    for child in children:
        assert child.parent_id is not None
        assert child.parent_id in id_map
        parent = id_map[child.parent_id]
        assert parent.chunk_type == ChunkType.PARENT.value


def test_validate_records_clean(full_corpus):
    errors = validate_records(full_corpus)
    assert errors == [], f"Validation errors: {errors}"


def test_reproducibility():
    """Same input must produce the same logical content (IDs may differ)."""
    a = process_document(BASELINE)
    b = process_document(BASELINE)

    # Same number of chunks and same sections / control_ids
    assert len(a) == len(b)
    a_keys = sorted((r.section, r.control_id, r.chunk_type) for r in a)
    b_keys = sorted((r.section, r.control_id, r.chunk_type) for r in b)
    assert a_keys == b_keys


# ---------------------------------------------------------------------------
# JSONL round-trip
# ---------------------------------------------------------------------------

def test_jsonl_roundtrip(full_corpus, tmp_path):
    out = tmp_path / "corpus.jsonl"
    write_jsonl(full_corpus, out)
    loaded = load_jsonl(out)

    assert len(loaded) == len(full_corpus)
    for original, restored in zip(full_corpus, loaded):
        assert original.chunk_id == restored.chunk_id
        assert original.text == restored.text
        assert original.control_id == restored.control_id
        assert original.asset_type == restored.asset_type


def test_jsonl_is_valid_json(full_corpus, tmp_path):
    out = tmp_path / "corpus.jsonl"
    write_jsonl(full_corpus, out)
    with out.open() as fh:
        for line in fh:
            obj = json.loads(line)
            assert "chunk_id" in obj
            assert "text" in obj
