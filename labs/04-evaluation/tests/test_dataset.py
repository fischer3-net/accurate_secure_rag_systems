"""Tests for golden dataset schema and fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.dataset import load_golden_dataset, validate_golden_dataset, load_fixture


GOLDEN = ROOT / "data" / "golden_dataset.jsonl"
FIXTURES = ROOT / "data" / "fixtures"


def test_golden_loads_and_has_20_plus():
    rows = load_golden_dataset(GOLDEN)
    assert len(rows) >= 20
    assert rows[0].id.startswith("G")


def test_validate_golden_clean():
    errors = validate_golden_dataset(GOLDEN, FIXTURES)
    assert errors == [], errors


def test_fixtures_exist():
    for name in ("dfd_partner_order.json", "dfd_syntax_error.json", "dfd_clean_internal.json"):
        dfd = load_fixture(FIXTURES, name)
        assert "nodes" in dfd and "edges" in dfd


def test_tags_and_status_values():
    rows = load_golden_dataset(GOLDEN)
    statuses = {r.expected_status for r in rows}
    assert statuses <= {"pass", "fail", "review", "n/a", "unknown"}
    assert any("policy" in r.tags for r in rows)
    assert any("structural" in r.tags for r in rows)
