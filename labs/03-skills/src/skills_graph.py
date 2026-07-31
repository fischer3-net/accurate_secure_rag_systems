"""
Skill: check_trust_boundary_paths

Finds ExternalEntity → DataStore paths that cross a trust boundary.
Self-contained BFS so this skill does not depend on the Week 2 package path.
"""

from __future__ import annotations

from collections import defaultdict, deque

from .schemas import (
    CheckTrustPathsInput,
    CheckTrustPathsOutput,
    DfdDocumentIn,
    TrustPathFinding,
)


def check_trust_boundary_paths(
    payload: CheckTrustPathsInput | dict,
) -> CheckTrustPathsOutput:
    """
    Discover data-flow paths from ExternalEntity nodes to DataStore nodes.

    When require_crosses_trust_boundary is true, only paths that cross a
    TrustBoundary (CROSSES edge or FLOWS_TO with crosses_boundary=true)
    are returned.
    """
    if isinstance(payload, dict):
        payload = CheckTrustPathsInput.model_validate(payload)
    dfd: DfdDocumentIn = payload.dfd

    nodes = {n.id: n for n in dfd.nodes}
    out: dict[str, list] = defaultdict(list)
    for e in dfd.edges:
        if e.type in ("FLOWS_TO", "CROSSES"):
            out[e.source].append(e)

    sources = [n.id for n in dfd.nodes if n.type == "ExternalEntity"]
    targets = {n.id for n in dfd.nodes if n.type == "DataStore"}

    findings: list[TrustPathFinding] = []

    for src in sources:
        queue: deque = deque()
        queue.append((src, [src], False))
        seen_depth: dict[str, int] = {src: 0}

        while queue:
            current, path, crossed = queue.popleft()
            if len(path) > 8:
                continue
            if current in targets and current != src:
                if payload.require_crosses_trust_boundary and not crossed:
                    pass
                else:
                    # Collect GOVERNED_BY control ids along the path
                    ctrls: list[str] = []
                    path_set = set(path)
                    for e in dfd.edges:
                        if e.type == "GOVERNED_BY" and e.source in path_set:
                            ctrls.append(e.target)
                    findings.append(
                        TrustPathFinding(
                            path=list(path),
                            crosses_trust_boundary=crossed,
                            governed_control_ids=sorted(set(ctrls)),
                        )
                    )

            for edge in out.get(current, []):
                nxt = edge.target
                if nxt not in nodes:
                    continue
                depth = len(path)
                if nxt in seen_depth and seen_depth[nxt] < depth:
                    continue
                seen_depth[nxt] = depth
                new_crossed = crossed or edge.type == "CROSSES"
                if edge.properties.get("crosses_boundary"):
                    new_crossed = True
                queue.append((nxt, path + [nxt], new_crossed))

    if not findings:
        summary = "No matching paths found."
    else:
        crossed_n = sum(1 for f in findings if f.crosses_trust_boundary)
        summary = (
            f"Found {len(findings)} path(s); "
            f"{crossed_n} cross a trust boundary."
        )

    return CheckTrustPathsOutput(
        path_count=len(findings),
        paths=findings,
        summary=summary,
    )


check_trust_boundary_paths.skill_name = "check_trust_boundary_paths"
check_trust_boundary_paths.skill_description = (
    "Find paths from ExternalEntity to DataStore that cross a trust boundary. "
    "Returns each path and any GOVERNED_BY control ids linked to nodes on the path."
)
check_trust_boundary_paths.input_model = CheckTrustPathsInput
check_trust_boundary_paths.output_model = CheckTrustPathsOutput
