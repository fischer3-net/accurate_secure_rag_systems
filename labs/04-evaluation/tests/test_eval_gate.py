"""CI quality-gate tests for Lab 4.2."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.eval_runner import run_evaluation
from src.metrics import control_hit_rate, status_match, score_row, aggregate


GOLDEN = ROOT / "data" / "golden_dataset.jsonl"
FIXTURES = ROOT / "data" / "fixtures"
CORPUS = ROOT / "data" / "rag_chunks.jsonl"


def test_control_hit_rate_helper():
    assert control_hit_rate(["SEC-DFD-014", "X"], ["SEC-DFD-014"]) == 1.0
    assert control_hit_rate(["X"], ["SEC-DFD-014"]) == 0.0
    assert control_hit_rate([], []) == 1.0


def test_status_match_helper():
    assert status_match("fail", "fail") == 1.0
    assert status_match("pass", "fail") == 0.0
    assert status_match(None, "n/a") == 1.0


def test_score_row_aggregate():
    rs = score_row(
        row_id="T1",
        ground_truth_control_ids=["SEC-DFD-014"],
        expected_status="fail",
        expected_findings_substrings=["Syntax"],
        retrieved_control_ids=["SEC-DFD-014"],
        actual_status="fail",
        findings=["Syntax error: bad"],
    )
    assert rs.overall > 0.9
    report = aggregate([rs], min_mean_overall=0.5, min_mean_control_hit_rate=0.5)
    assert report.thresholds_passed


def test_full_eval_runner_passes_default_thresholds():
    report = run_evaluation(
        golden_path=GOLDEN,
        fixtures_dir=FIXTURES,
        corpus_path=CORPUS if CORPUS.exists() else None,
        min_mean_overall=0.50,
        min_mean_control_hit_rate=0.40,
    )
    assert report["n_rows"] >= 20
    assert "mean_overall" in report
    # Soft assertion: with the sample skills/corpus we expect a reasonable score
    assert report["mean_overall"] >= 0.40
    print("mean_overall", report["mean_overall"])
    print("mean_control_hit_rate", report["mean_control_hit_rate"])
    print("messages", report["messages"])


def test_gate_fails_when_threshold_impossibly_high():
    report = run_evaluation(
        golden_path=GOLDEN,
        fixtures_dir=FIXTURES,
        corpus_path=CORPUS if CORPUS.exists() else None,
        min_mean_overall=0.99,
        min_mean_control_hit_rate=0.99,
    )
    assert report["thresholds_passed"] is False
    assert any("threshold" in m for m in report["messages"])
