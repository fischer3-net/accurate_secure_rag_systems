"""
Skill: score_sdlc_compliance

Rule-based aggregator that turns prior skill outputs into an overall
compliance status. Deterministic and auditable.
"""

from __future__ import annotations

from .schemas import (
    ComplianceStatus,
    ControlResult,
    ScoreComplianceInput,
    ScoreComplianceOutput,
)


def score_sdlc_compliance(
    payload: ScoreComplianceInput | dict,
) -> ScoreComplianceOutput:
    """
    Aggregate syntax, trust-path, and policy results into a compliance score.

    Rules (intentionally simple for the lab):
    - Syntax errors → overall FAIL
    - Paths that cross a trust boundary with no governed controls → FAIL
    - Paths that cross a boundary with controls → REVIEW (need human check)
    - No structural issues + some policy matches → PASS / REVIEW
    """
    if isinstance(payload, dict):
        payload = ScoreComplianceInput.model_validate(payload)

    findings: list[str] = []
    control_results: list[ControlResult] = []
    status = ComplianceStatus.PASS

    # Syntax
    if payload.syntax is not None:
        if not payload.syntax.ok:
            status = ComplianceStatus.FAIL
            for issue in payload.syntax.issues:
                if issue.severity == "error":
                    findings.append(f"Syntax error: {issue.message}")
        else:
            findings.append("DFD syntax validation passed.")

    # Trust paths
    if payload.trust_paths is not None:
        if payload.trust_paths.path_count == 0:
            findings.append("No ExternalEntity→DataStore trust-boundary paths found.")
        for p in payload.trust_paths.paths:
            route = " → ".join(p.path)
            if p.crosses_trust_boundary and not p.governed_control_ids:
                status = ComplianceStatus.FAIL
                findings.append(
                    f"Uncontrolled trust-boundary path: {route}"
                )
            elif p.crosses_trust_boundary:
                if status == ComplianceStatus.PASS:
                    status = ComplianceStatus.REVIEW
                findings.append(
                    f"Trust-boundary path under controls {p.governed_control_ids}: {route}"
                )
                for cid in p.governed_control_ids:
                    control_results.append(
                        ControlResult(
                            control_id=cid,
                            status=ComplianceStatus.REVIEW,
                            rationale=f"Governs path {route}",
                        )
                    )

    # Policy matches
    if payload.policy_matches is not None:
        if not payload.policy_matches.matches:
            findings.append("No policy controls matched the query.")
            if status == ComplianceStatus.PASS:
                status = ComplianceStatus.REVIEW
        else:
            for m in payload.policy_matches.matches:
                if m.control_id:
                    control_results.append(
                        ControlResult(
                            control_id=m.control_id,
                            status=ComplianceStatus.REVIEW,
                            rationale=f"Matched query with score {m.score:.2f}",
                        )
                    )

    # De-dupe control results by control_id (keep first)
    seen: set[str] = set()
    unique_controls: list[ControlResult] = []
    for cr in control_results:
        if cr.control_id not in seen:
            seen.add(cr.control_id)
            unique_controls.append(cr)

    risk_summary = {
        ComplianceStatus.PASS: "No critical structural or syntax issues detected.",
        ComplianceStatus.REVIEW: "Structural or policy items require human review.",
        ComplianceStatus.FAIL: "Critical syntax or uncontrolled trust-boundary paths found.",
        ComplianceStatus.UNKNOWN: "Insufficient data to score.",
    }[status]

    return ScoreComplianceOutput(
        overall_status=status,
        control_results=unique_controls,
        findings=findings,
        risk_summary=risk_summary,
    )


score_sdlc_compliance.skill_name = "score_sdlc_compliance"
score_sdlc_compliance.skill_description = (
    "Aggregate syntax, trust-path, and policy-match results into an overall "
    "compliance status with findings and per-control outcomes."
)
score_sdlc_compliance.input_model = ScoreComplianceInput
score_sdlc_compliance.output_model = ScoreComplianceOutput
