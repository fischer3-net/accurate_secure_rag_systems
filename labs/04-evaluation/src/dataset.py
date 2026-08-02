"""
Golden dataset loader and schema validation for Lab 4.1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


ALLOWED_STATUS = {"pass", "fail", "review", "n/a", "unknown"}


class GoldenRow(BaseModel):
    id: str
    question: str
    dfd_fixture: Optional[str] = None
    ground_truth_control_ids: list[str] = Field(default_factory=list)
    expected_status: str = "n/a"
    expected_findings_substrings: list[str] = Field(default_factory=list)
    ground_truth_contexts: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    @field_validator("expected_status")
    @classmethod
    def status_ok(cls, v: str) -> str:
        if v not in ALLOWED_STATUS:
            raise ValueError(f"expected_status must be one of {ALLOWED_STATUS}")
        return v

    @field_validator("id")
    @classmethod
    def id_nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("id must be non-empty")
        return v


def load_golden_dataset(path: Path | str) -> list[GoldenRow]:
    path = Path(path)
    rows: list[GoldenRow] = []
    with path.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(GoldenRow.model_validate(json.loads(line)))
            except Exception as e:
                raise ValueError(f"Invalid golden row at line {i}: {e}") from e
    return rows


def validate_golden_dataset(
    path: Path | str,
    fixtures_dir: Optional[Path | str] = None,
) -> list[str]:
    """
    Return a list of human-readable errors (empty list == valid).
    """
    errors: list[str] = []
    try:
        rows = load_golden_dataset(path)
    except ValueError as e:
        return [str(e)]

    if len(rows) < 20:
        errors.append(f"Expected ≥20 rows, found {len(rows)}")

    ids = [r.id for r in rows]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate ids in golden dataset")

    fixtures_dir = Path(fixtures_dir) if fixtures_dir else Path(path).parent / "fixtures"
    for r in rows:
        if r.dfd_fixture:
            fp = fixtures_dir / r.dfd_fixture
            if not fp.exists():
                errors.append(f"{r.id}: missing fixture {r.dfd_fixture}")
        if not r.question.strip():
            errors.append(f"{r.id}: empty question")

    return errors


def load_fixture(fixtures_dir: Path | str, name: str) -> dict[str, Any]:
    path = Path(fixtures_dir) / name
    return json.loads(path.read_text(encoding="utf-8"))
