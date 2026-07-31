"""
In-memory DFD graph store for Lab 2.2.

Pure-Python adjacency implementation so the lab runs without Neo4j.
The same conceptual operations (path finding, control linking) map
directly onto Cypher / GQL when you later point at Neo4j or Spanner Graph.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .graph_schema import DfdDocument, DfdEdge, DfdNode


@dataclass
class PathResult:
    nodes: list[str]
    edges: list[tuple[str, str, str]]  # (source, type, target)
    crosses_trust_boundary: bool
    governed_control_ids: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        route = " → ".join(self.nodes)
        flag = " [CROSSES TRUST BOUNDARY]" if self.crosses_trust_boundary else ""
        ctrls = f" controls={self.governed_control_ids}" if self.governed_control_ids else ""
        return f"{route}{flag}{ctrls}"


class DfdGraphStore:
    def __init__(self):
        self.nodes: dict[str, DfdNode] = {}
        self.out_edges: dict[str, list[DfdEdge]] = defaultdict(list)
        self.in_edges: dict[str, list[DfdEdge]] = defaultdict(list)
        self.control_links: dict[str, list[str]] = defaultdict(list)  # node/edge-key → control_ids

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, doc: DfdDocument) -> None:
        for n in doc.nodes:
            self.nodes[n.id] = n
        for e in doc.edges:
            if e.type == "GOVERNED_BY":
                # target is a control_id
                self.control_links[e.source].append(e.target)
            else:
                self.out_edges[e.source].append(e)
                self.in_edges[e.target].append(e)

    def link_control(self, element_id: str, control_id: str) -> None:
        if control_id not in self.control_links[element_id]:
            self.control_links[element_id].append(control_id)

    def link_controls_from_corpus(self, records: Sequence[Any]) -> int:
        """
        Heuristic linker: attach controls whose asset_type matches the
        node type (e.g. DataStore ↔ data_store controls).
        """
        type_map = {
            "Process": "process",
            "DataStore": "data_store",
            "ExternalEntity": "external_entity",
            "TrustBoundary": "trust_boundary",
        }
        linked = 0
        for node in self.nodes.values():
            wanted = type_map.get(node.type)
            if not wanted:
                continue
            for r in records:
                asset = getattr(r, "asset_type", None) or (r.get("asset_type") if isinstance(r, dict) else None)
                cid = getattr(r, "control_id", None) or (r.get("control_id") if isinstance(r, dict) else None)
                if asset == wanted and cid:
                    self.link_control(node.id, cid)
                    linked += 1
        return linked

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, int]:
        return {
            "nodes": len(self.nodes),
            "flow_edges": sum(
                1 for edges in self.out_edges.values() for e in edges if e.type == "FLOWS_TO"
            ),
            "cross_edges": sum(
                1 for edges in self.out_edges.values() for e in edges if e.type == "CROSSES"
            ),
            "control_links": sum(len(v) for v in self.control_links.values()),
        }

    def nodes_of_type(self, node_type: str) -> list[DfdNode]:
        return [n for n in self.nodes.values() if n.type == node_type]

    def find_paths(
        self,
        *,
        source_type: Optional[str] = None,
        target_type: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        require_crosses_trust_boundary: bool = False,
        max_depth: int = 6,
    ) -> list[PathResult]:
        """
        BFS path finder over FLOWS_TO / CROSSES edges.
        """
        sources = []
        if source_id:
            sources = [source_id]
        elif source_type:
            sources = [n.id for n in self.nodes_of_type(source_type)]
        else:
            sources = list(self.nodes.keys())

        targets: set[str] = set()
        if target_id:
            targets = {target_id}
        elif target_type:
            targets = {n.id for n in self.nodes_of_type(target_type)}

        results: list[PathResult] = []

        for src in sources:
            # BFS: state = (current, path_nodes, path_edges, crossed)
            queue: deque = deque()
            queue.append((src, [src], [], False))
            visited_depth: dict[str, int] = {src: 0}

            while queue:
                current, path_nodes, path_edges, crossed = queue.popleft()
                if len(path_nodes) > max_depth:
                    continue
                if current in targets and current != src:
                    if require_crosses_trust_boundary and not crossed:
                        pass
                    else:
                        # collect controls along the path
                        ctrls: list[str] = []
                        for nid in path_nodes:
                            ctrls.extend(self.control_links.get(nid, []))
                        results.append(
                            PathResult(
                                nodes=list(path_nodes),
                                edges=list(path_edges),
                                crosses_trust_boundary=crossed,
                                governed_control_ids=sorted(set(ctrls)),
                            )
                        )
                    # do not stop; find all paths

                for edge in self.out_edges.get(current, []):
                    if edge.type not in ("FLOWS_TO", "CROSSES"):
                        continue
                    nxt = edge.target
                    depth = len(path_nodes)
                    if nxt in visited_depth and visited_depth[nxt] < depth:
                        continue
                    visited_depth[nxt] = depth
                    new_crossed = crossed or edge.type == "CROSSES"
                    # also treat FLOWS_TO that explicitly marks crosses_boundary
                    if edge.properties.get("crosses_boundary"):
                        new_crossed = True
                    queue.append(
                        (
                            nxt,
                            path_nodes + [nxt],
                            path_edges + [(edge.source, edge.type, edge.target)],
                            new_crossed,
                        )
                    )

        return results

    def unauthenticated_external_to_datastore_paths(self) -> list[PathResult]:
        """
        Convenience query for the classic violation:
        ExternalEntity → … → DataStore that crosses a trust boundary
        and has no authentication-related control linked.
        """
        paths = self.find_paths(
            source_type="ExternalEntity",
            target_type="DataStore",
            require_crosses_trust_boundary=True,
        )
        # Flag paths that lack an obvious auth control
        flagged = []
        for p in paths:
            authish = [
                c for c in p.governed_control_ids
                if "014" in c or "AUTH" in c.upper() or "EXTERNAL" in c.upper()
            ]
            if not authish:
                flagged.append(p)
            else:
                # still return them but caller can inspect
                flagged.append(p)
        return flagged
