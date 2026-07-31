"""
Skill: match_security_controls

Hybrid-style control lookup over a pre-loaded corpus of ChunkRecord dicts.
Works offline with the exported Week 1 JSONL; can be pointed at a live
HybridRetriever later without changing the skill signature.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any, Optional

from .schemas import (
    MatchControlsInput,
    MatchControlsOutput,
    MatchedControl,
)

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.I)


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _hash_embed(text: str, dim: int = 128) -> list[float]:
    vec = [0.0] * dim
    for tok in _tokenize(text):
        h = hash(tok) % dim
        sign = 1.0 if hash(tok + "s") % 2 == 0 else -1.0
        vec[h] += sign
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class ControlCorpus:
    """Simple in-memory corpus for the policy skill."""

    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self._vecs: list[list[float]] = []

    def load_jsonl(self, path: Path | str) -> int:
        path = Path(path)
        self.rows.clear()
        self._vecs.clear()
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            self.rows.append(row)
            self._vecs.append(_hash_embed(row.get("text", "")))
        return len(self.rows)

    def load_records(self, records: list[Any]) -> int:
        self.rows.clear()
        self._vecs.clear()
        for r in records:
            if hasattr(r, "to_dict"):
                d = r.to_dict()
            elif hasattr(r, "model_dump"):
                d = r.model_dump()
            else:
                d = dict(r)
            self.rows.append(d)
            self._vecs.append(_hash_embed(d.get("text", "")))
        return len(self.rows)


# Module-level default corpus (populated by notebook / tests)
_CORPUS = ControlCorpus()


def set_policy_corpus(corpus: ControlCorpus) -> None:
    global _CORPUS
    _CORPUS = corpus


def match_security_controls(
    payload: MatchControlsInput | dict,
) -> MatchControlsOutput:
    """
    Retrieve security controls relevant to a natural-language query.

    Supports optional metadata filters (asset_type, risk_tier).
    """
    if isinstance(payload, dict):
        payload = MatchControlsInput.model_validate(payload)

    q_vec = _hash_embed(payload.query)
    scored: list[tuple[float, dict]] = []
    for row, vec in zip(_CORPUS.rows, _CORPUS._vecs):
        if payload.asset_type and row.get("asset_type") != payload.asset_type:
            continue
        if payload.risk_tier and row.get("risk_tier") != payload.risk_tier:
            continue
        score = _cosine(q_vec, vec)
        # Light BM25-style boost for exact control id in query
        cid = row.get("control_id") or ""
        if cid and cid.upper() in payload.query.upper():
            score += 0.25
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    matches: list[MatchedControl] = []
    for score, row in scored[: payload.top_k]:
        if score <= 0:
            continue
        matches.append(
            MatchedControl(
                control_id=row.get("control_id"),
                section=row.get("section"),
                score=float(score),
                text_preview=(row.get("text") or "")[:180],
            )
        )

    return MatchControlsOutput(query=payload.query, matches=matches)


match_security_controls.skill_name = "match_security_controls"
match_security_controls.skill_description = (
    "Retrieve security controls relevant to a query, with optional "
    "asset_type / risk_tier filters. Returns ranked control_id, section, score."
)
match_security_controls.input_model = MatchControlsInput
match_security_controls.output_model = MatchControlsOutput
