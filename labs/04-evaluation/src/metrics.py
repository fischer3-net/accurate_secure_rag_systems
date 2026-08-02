"""
Deterministic evaluation metrics for Lab 4.

These metrics run offline without an LLM judge. They are the hard quality
gate used in CI. Optional Ragas / Vertex judge scores can be layered on later.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence


def control_hit_rate(
    retrieved_control_ids: Sequence[Optional[str]],
    ground_truth_control_ids: Sequence[str],
) -> float:
    """1.0 if every ground-truth control id appears in retrieved, else fraction found."""
    if not ground_truth_control_ids:
        return 1.0
    got = {c for c in retrieved_control_ids if c}
    hits = sum(1 for g in ground_truth_control_ids if g in got)
    return hits / len(ground_truth_control_ids)


def status_match(actual: Optional[str], expected: str) -> float:
    if expected in ("n/a", "unknown"):
        return 1.0  # status not scored for policy-only rows
    if actual is None:
        return 0.0
    return 1.0 if actual.lower() == expected.lower() else 0.0


def findings_substring_score(
    findings: Sequence[str],
    expected_substrings: Sequence[str],
) -> float:
    if not expected_substrings:
        return 1.0
    blob = " ".join(findings).lower()
    hits = sum(1 for s in expected_substrings if s.lower() in blob)
    return hits / len(expected_substrings)


@dataclass
class RowScore:
    id: str
    control_hit_rate: float
    status_match: float
    findings_score: float
    overall: float
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalReport:
    n_rows: int
    mean_control_hit_rate: float
    mean_status_match: float
    mean_findings_score: float
    mean_overall: float
    row_scores: list[RowScore] = field(default_factory=list)
    thresholds_passed: bool = True
    messages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_rows": self.n_rows,
            "mean_control_hit_rate": self.mean_control_hit_rate,
            "mean_status_match": self.mean_status_match,
            "mean_findings_score": self.mean_findings_score,
            "mean_overall": self.mean_overall,
            "thresholds_passed": self.thresholds_passed,
            "messages": self.messages,
            "row_scores": [
                {
                    "id": r.id,
                    "control_hit_rate": r.control_hit_rate,
                    "status_match": r.status_match,
                    "findings_score": r.findings_score,
                    "overall": r.overall,
                    "detail": r.detail,
                }
                for r in self.row_scores
            ],
        }


def score_row(
    *,
    row_id: str,
    ground_truth_control_ids: Sequence[str],
    expected_status: str,
    expected_findings_substrings: Sequence[str],
    retrieved_control_ids: Sequence[Optional[str]],
    actual_status: Optional[str],
    findings: Sequence[str],
) -> RowScore:
    chr_ = control_hit_rate(retrieved_control_ids, ground_truth_control_ids)
    sm = status_match(actual_status, expected_status)
    fs = findings_substring_score(findings, expected_findings_substrings)
    # Weight: controls and status matter most for compliance
    overall = 0.45 * chr_ + 0.35 * sm + 0.20 * fs
    return RowScore(
        id=row_id,
        control_hit_rate=chr_,
        status_match=sm,
        findings_score=fs,
        overall=overall,
        detail={
            "retrieved_control_ids": list(retrieved_control_ids),
            "actual_status": actual_status,
            "findings": list(findings),
        },
    )


def aggregate(
    row_scores: Sequence[RowScore],
    *,
    min_mean_overall: float = 0.70,
    min_mean_control_hit_rate: float = 0.60,
) -> EvalReport:
    n = len(row_scores) or 1
    mean_chr = sum(r.control_hit_rate for r in row_scores) / n
    mean_sm = sum(r.status_match for r in row_scores) / n
    mean_fs = sum(r.findings_score for r in row_scores) / n
    mean_ov = sum(r.overall for r in row_scores) / n

    messages = []
    passed = True
    if mean_ov < min_mean_overall:
        passed = False
        messages.append(
            f"mean_overall {mean_ov:.3f} < threshold {min_mean_overall}"
        )
    if mean_chr < min_mean_control_hit_rate:
        passed = False
        messages.append(
            f"mean_control_hit_rate {mean_chr:.3f} < threshold {min_mean_control_hit_rate}"
        )
    if passed:
        messages.append("All configured thresholds passed.")

    return EvalReport(
        n_rows=len(row_scores),
        mean_control_hit_rate=mean_chr,
        mean_status_match=mean_sm,
        mean_findings_score=mean_fs,
        mean_overall=mean_ov,
        row_scores=list(row_scores),
        thresholds_passed=passed,
        messages=messages,
    )
