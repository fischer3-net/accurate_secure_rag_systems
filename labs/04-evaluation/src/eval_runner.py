"""
Headless evaluation runner for Lab 4.2 / CI.

Runs the Week 3 skill stack against the golden dataset and produces a
metrics report. Works offline.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

# Local imports
from .dataset import GoldenRow, load_fixture, load_golden_dataset
from .metrics import RowScore, aggregate, score_row


def _week3_src_path() -> Path:
    return Path(__file__).resolve().parents[2] / "03-skills" / "src"


def _import_week3():
    """
    Temporarily map the name `src` to Week 3's src package so skill modules
    (which use relative imports) load correctly, then restore any prior mapping.
    """
    import importlib
    import types

    week3_src = _week3_src_path()
    week3_root = week3_src.parent

    # Ensure week3 root is importable
    if str(week3_root) not in sys.path:
        sys.path.insert(0, str(week3_root))

    prior_src = sys.modules.get("src")
    prior_sub = {k: v for k, v in sys.modules.items() if k == "src" or k.startswith("src.")}

    # Build a package module for week3 src
    pkg = types.ModuleType("src")
    pkg.__path__ = [str(week3_src)]
    pkg.__file__ = str(week3_src / "__init__.py")
    sys.modules["src"] = pkg

    # Clear any cached week4 src.* modules that would shadow week3
    for k in list(sys.modules.keys()):
        if k.startswith("src.") and k not in ("src",):
            # Only drop if the file lives under 04-evaluation
            mod = sys.modules[k]
            f = getattr(mod, "__file__", "") or ""
            if "04-evaluation" in str(f).replace(chr(92), "/"):
                del sys.modules[k]

    importlib.invalidate_caches()
    schemas = importlib.import_module("src.schemas")
    skills_syntax = importlib.import_module("src.skills_syntax")
    skills_graph = importlib.import_module("src.skills_graph")
    skills_policy = importlib.import_module("src.skills_policy")
    skills_score = importlib.import_module("src.skills_score")

    return schemas, skills_syntax, skills_graph, skills_policy, skills_score


def _run_skills_on_row(
    row: GoldenRow,
    fixtures_dir: Path,
    corpus_loaded: bool,
) -> tuple[list[Optional[str]], Optional[str], list[str]]:
    """
    Execute the relevant Week 3 skills for one golden row.
    Returns (retrieved_control_ids, actual_status, findings).
    """
    schemas, skills_syntax, skills_graph, skills_policy, skills_score = _import_week3()
    validate_dfd_syntax = skills_syntax.validate_dfd_syntax
    check_trust_boundary_paths = skills_graph.check_trust_boundary_paths
    match_security_controls = skills_policy.match_security_controls
    score_sdlc_compliance = skills_score.score_sdlc_compliance
    ValidateDfdInput = schemas.ValidateDfdInput
    CheckTrustPathsInput = schemas.CheckTrustPathsInput
    MatchControlsInput = schemas.MatchControlsInput
    ScoreComplianceInput = schemas.ScoreComplianceInput

    retrieved: list[Optional[str]] = []
    findings: list[str] = []
    actual_status: Optional[str] = None
    syn_out = None
    path_out = None
    pol_out = None

    dfd = None
    if row.dfd_fixture:
        dfd = load_fixture(fixtures_dir, row.dfd_fixture)
        syn_out = validate_dfd_syntax(ValidateDfdInput.model_validate({"dfd": dfd}))
        if not syn_out.ok:
            findings.extend(f"Syntax error: {i.message}" for i in syn_out.issues if i.severity == "error")
        else:
            findings.append("DFD syntax validation passed.")

        path_out = check_trust_boundary_paths(
            CheckTrustPathsInput.model_validate(
                {"dfd": dfd, "require_crosses_trust_boundary": True}
            )
        )
        findings.append(path_out.summary)
        for p in path_out.paths:
            retrieved.extend(p.governed_control_ids)
            if p.crosses_trust_boundary:
                findings.append(
                    f"trust-boundary path: {' → '.join(p.path)}"
                )

    # Policy match (always useful when we have a question)
    if corpus_loaded:
        pol_out = match_security_controls(
            MatchControlsInput(query=row.question, top_k=5)
        )
        for m in pol_out.matches:
            if m.control_id:
                retrieved.append(m.control_id)

    score_out = score_sdlc_compliance(
        ScoreComplianceInput(
            syntax=syn_out,
            trust_paths=path_out,
            policy_matches=pol_out,
        )
    )
    actual_status = score_out.overall_status.value
    findings.extend(score_out.findings)

    # De-dupe retrieved ids preserving order
    seen = set()
    uniq: list[Optional[str]] = []
    for c in retrieved:
        if c and c not in seen:
            seen.add(c)
            uniq.append(c)

    return uniq, actual_status, findings


def run_evaluation(
    *,
    golden_path: Path | str,
    fixtures_dir: Path | str,
    corpus_path: Optional[Path | str] = None,
    min_mean_overall: float = 0.55,
    min_mean_control_hit_rate: float = 0.50,
    limit: Optional[int] = None,
) -> dict[str, Any]:
    golden_path = Path(golden_path)
    fixtures_dir = Path(fixtures_dir)
    rows = load_golden_dataset(golden_path)
    if limit is not None:
        rows = rows[:limit]

    corpus_loaded = False
    if corpus_path and Path(corpus_path).exists():
        _, _, _, skills_policy, _ = _import_week3()
        corpus = skills_policy.ControlCorpus()
        corpus.load_jsonl(corpus_path)
        skills_policy.set_policy_corpus(corpus)
        corpus_loaded = True

    row_scores: list[RowScore] = []
    for row in rows:
        try:
            retrieved, status, findings = _run_skills_on_row(
                row, fixtures_dir, corpus_loaded
            )
        except Exception as e:
            retrieved, status, findings = [], None, [f"runner error: {e}"]

        rs = score_row(
            row_id=row.id,
            ground_truth_control_ids=row.ground_truth_control_ids,
            expected_status=row.expected_status,
            expected_findings_substrings=row.expected_findings_substrings,
            retrieved_control_ids=retrieved,
            actual_status=status,
            findings=findings,
        )
        row_scores.append(rs)

    report = aggregate(
        row_scores,
        min_mean_overall=min_mean_overall,
        min_mean_control_hit_rate=min_mean_control_hit_rate,
    )
    return report.to_dict()


def main(argv: Optional[list[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run Lab 4 evaluation suite")
    root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--golden",
        default=str(root / "data" / "golden_dataset.jsonl"),
    )
    parser.add_argument(
        "--fixtures",
        default=str(root / "data" / "fixtures"),
    )
    parser.add_argument(
        "--corpus",
        default=str(root / "data" / "rag_chunks.jsonl"),
    )
    parser.add_argument("--output", default=str(root / "output" / "metrics.json"))
    parser.add_argument("--min-overall", type=float, default=0.55)
    parser.add_argument("--min-hit-rate", type=float, default=0.50)
    args = parser.parse_args(argv)

    report = run_evaluation(
        golden_path=args.golden,
        fixtures_dir=args.fixtures,
        corpus_path=args.corpus,
        min_mean_overall=args.min_overall,
        min_mean_control_hit_rate=args.min_hit_rate,
    )

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k != "row_scores"}, indent=2))
    print(f"Wrote {out}")

    return 0 if report["thresholds_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
