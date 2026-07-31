"""Unit tests for Lab 3.1 modular skills."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.skills_syntax import validate_dfd_syntax
from src.skills_graph import check_trust_boundary_paths
from src.skills_policy import match_security_controls, set_policy_corpus, ControlCorpus
from src.skills_score import score_sdlc_compliance
from src.registry import build_default_registry
from src.mega_prompt import mega_prompt_token_estimate
from src.schemas import (
    ValidateDfdInput,
    CheckTrustPathsInput,
    MatchControlsInput,
    ScoreComplianceInput,
    ComplianceStatus,
)


@pytest.fixture(scope="module")
def sample_dfd():
    path = ROOT / "data" / "sample_dfd.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def corpus_loaded():
    corpus = ControlCorpus()
    path = ROOT / "data" / "rag_chunks.jsonl"
    if path.exists():
        corpus.load_jsonl(path)
    set_policy_corpus(corpus)
    return corpus


def test_validate_syntax_ok(sample_dfd):
    out = validate_dfd_syntax(ValidateDfdInput.model_validate({"dfd": sample_dfd}))
    assert out.ok is True
    assert out.node_count >= 4


def test_validate_syntax_detects_bad_type(sample_dfd):
    bad = json.loads(json.dumps(sample_dfd))
    bad["nodes"].append(
        {"id": "x", "type": "NotARealType", "name": "X", "properties": {}}
    )
    out = validate_dfd_syntax({"dfd": bad})
    assert out.ok is False
    assert any(i.code == "INVALID_NODE_TYPE" for i in out.issues)


def test_trust_paths_find_crossing(sample_dfd):
    out = check_trust_boundary_paths(
        CheckTrustPathsInput.model_validate(
            {"dfd": sample_dfd, "require_crosses_trust_boundary": True}
        )
    )
    assert out.path_count >= 1
    assert any(p.crosses_trust_boundary for p in out.paths)


def test_match_controls(corpus_loaded):
    if corpus_loaded.rows == []:
        pytest.skip("no corpus")
    out = match_security_controls(
        MatchControlsInput(query="external entity write access to data store", top_k=3)
    )
    assert len(out.matches) >= 1


def test_score_fail_on_syntax_error(sample_dfd):
    syn = validate_dfd_syntax({"dfd": sample_dfd})
    # force a fake failure
    syn.ok = False
    syn.issues = []
    from src.schemas import SyntaxIssue

    syn.issues.append(
        SyntaxIssue(severity="error", code="X", message="forced")
    )
    out = score_sdlc_compliance(
        ScoreComplianceInput(syntax=syn, trust_paths=None, policy_matches=None)
    )
    assert out.overall_status == ComplianceStatus.FAIL


def test_registry_declarations():
    reg = build_default_registry()
    decls = reg.vertex_tool_declarations()
    names = {d["name"] for d in decls}
    assert "validate_dfd_syntax" in names
    assert "score_sdlc_compliance" in names
    for d in decls:
        assert "parameters" in d
        assert d["parameters"]["type"] == "object"


def test_mega_prompt_is_large(sample_dfd):
    tokens = mega_prompt_token_estimate(sample_dfd)
    # Should be substantially larger than a single skill schema
    assert tokens > 200
