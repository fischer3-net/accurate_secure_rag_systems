"""
Minimal DFD graph schema for Lab 2.2.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


ALLOWED_NODE_TYPES = {"Process", "DataStore", "ExternalEntity", "TrustBoundary"}
ALLOWED_EDGE_TYPES = {"FLOWS_TO", "CROSSES", "GOVERNED_BY"}


@dataclass
class DfdNode:
    id: str
    type: str
    name: str
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.type not in ALLOWED_NODE_TYPES:
            raise ValueError(f"Unknown node type: {self.type}")


@dataclass
class DfdEdge:
    source: str
    target: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.type not in ALLOWED_EDGE_TYPES:
            raise ValueError(f"Unknown edge type: {self.type}")


@dataclass
class DfdDocument:
    """A complete DFD ready for ingestion into the graph store."""
    name: str
    nodes: list[DfdNode]
    edges: list[DfdEdge]
    description: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        ids = {n.id for n in self.nodes}
        for e in self.edges:
            if e.source not in ids and e.type != "GOVERNED_BY":
                # GOVERNED_BY may point at external control ids
                if e.type in ("FLOWS_TO", "CROSSES"):
                    errors.append(f"Edge source not found: {e.source}")
            if e.target not in ids and e.type in ("FLOWS_TO", "CROSSES"):
                errors.append(f"Edge target not found: {e.target}")
        return errors


def load_dfd_json(path: Path | str) -> DfdDocument:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    nodes = [DfdNode(**n) for n in raw["nodes"]]
    edges = [DfdEdge(**e) for e in raw["edges"]]
    doc = DfdDocument(
        name=raw.get("name", "unnamed"),
        description=raw.get("description", ""),
        nodes=nodes,
        edges=edges,
    )
    errs = doc.validate()
    if errs:
        raise ValueError("Invalid DFD: " + "; ".join(errs))
    return doc
