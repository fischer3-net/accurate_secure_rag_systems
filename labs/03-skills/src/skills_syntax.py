"""
Skill: validate_dfd_syntax

Deterministic structural / referential checks on a DFD document.
No LLM involved – cannot be prompt-injected.
"""

from __future__ import annotations

from .schemas import (
    DfdDocumentIn,
    SyntaxIssue,
    ValidateDfdInput,
    ValidateDfdOutput,
)

ALLOWED_NODE_TYPES = {"Process", "DataStore", "ExternalEntity", "TrustBoundary"}
ALLOWED_EDGE_TYPES = {"FLOWS_TO", "CROSSES", "GOVERNED_BY"}


def validate_dfd_syntax(payload: ValidateDfdInput | dict) -> ValidateDfdOutput:
    """
    Validate DFD JSON structure and referential integrity.

    Checks:
    - Required fields present
    - Node / edge types in the allowed set
    - FLOWS_TO / CROSSES endpoints reference existing nodes
    - Duplicate node ids
    """
    if isinstance(payload, dict):
        payload = ValidateDfdInput.model_validate(payload)
    dfd: DfdDocumentIn = payload.dfd
    issues: list[SyntaxIssue] = []

    ids = [n.id for n in dfd.nodes]
    if len(ids) != len(set(ids)):
        issues.append(
            SyntaxIssue(
                severity="error",
                code="DUPLICATE_NODE_ID",
                message="Duplicate node ids detected",
            )
        )

    id_set = set(ids)
    for n in dfd.nodes:
        if n.type not in ALLOWED_NODE_TYPES:
            issues.append(
                SyntaxIssue(
                    severity="error",
                    code="INVALID_NODE_TYPE",
                    message=f"Node {n.id} has invalid type {n.type!r}",
                    path=n.id,
                )
            )
        if not n.name.strip():
            issues.append(
                SyntaxIssue(
                    severity="warning",
                    code="EMPTY_NODE_NAME",
                    message=f"Node {n.id} has an empty name",
                    path=n.id,
                )
            )

    for i, e in enumerate(dfd.edges):
        if e.type not in ALLOWED_EDGE_TYPES:
            issues.append(
                SyntaxIssue(
                    severity="error",
                    code="INVALID_EDGE_TYPE",
                    message=f"Edge[{i}] has invalid type {e.type!r}",
                )
            )
        if e.type in ("FLOWS_TO", "CROSSES"):
            if e.source not in id_set:
                issues.append(
                    SyntaxIssue(
                        severity="error",
                        code="MISSING_SOURCE",
                        message=f"Edge[{i}] source {e.source!r} not found",
                    )
                )
            if e.target not in id_set:
                issues.append(
                    SyntaxIssue(
                        severity="error",
                        code="MISSING_TARGET",
                        message=f"Edge[{i}] target {e.target!r} not found",
                    )
                )

    errors = [x for x in issues if x.severity == "error"]
    return ValidateDfdOutput(
        ok=len(errors) == 0,
        issues=issues,
        node_count=len(dfd.nodes),
        edge_count=len(dfd.edges),
    )


# Metadata for the registry
validate_dfd_syntax.skill_name = "validate_dfd_syntax"
validate_dfd_syntax.skill_description = (
    "Validate DFD JSON structure, node/edge types, and referential integrity. "
    "Returns ok=false with typed issues when the diagram is malformed."
)
validate_dfd_syntax.input_model = ValidateDfdInput
validate_dfd_syntax.output_model = ValidateDfdOutput
