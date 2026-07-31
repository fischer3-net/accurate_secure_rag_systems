"""
Graph-Augmented RAG: structural findings + policy retrieval.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from .graph_store import DfdGraphStore, PathResult


@dataclass
class GraphRAGAnswer:
    question: str
    structural_findings: list[str]
    policy_hits: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""


class GraphRAG:
    """
    Combines DfdGraphStore path finding with any Week-1-style retriever
    that exposes a `.retrieve(query, top_k=...)` or `.search(...)` method.
    """

    def __init__(self, graph: DfdGraphStore, retriever: Any = None):
        self.graph = graph
        self.retriever = retriever

    def structural_scan(self) -> list[PathResult]:
        return self.graph.unauthenticated_external_to_datastore_paths()

    def ask(self, question: str, *, top_k: int = 3) -> GraphRAGAnswer:
        # 1. Structural half
        paths = self.structural_scan()
        findings = [str(p) for p in paths]

        # 2. Collect control ids discovered on those paths
        control_ids: list[str] = []
        for p in paths:
            control_ids.extend(p.governed_control_ids)
        control_ids = sorted(set(control_ids))

        # 3. Semantic / hybrid retrieval for policy text
        policy_hits: list[dict[str, Any]] = []
        if self.retriever is not None:
            # Prefer a retrieve() API (Week 1 HybridRetriever) then search()
            if hasattr(self.retriever, "retrieve"):
                result = self.retriever.retrieve(question, top_k=top_k)
                hits = getattr(result, "final_hits", []) or []
                for h in hits:
                    policy_hits.append(
                        {
                            "control_id": getattr(h, "control_id", None),
                            "score": getattr(h, "score", None),
                            "section": getattr(getattr(h, "record", None), "section", None),
                            "text": (getattr(h, "text", None) or "")[:200],
                        }
                    )
            elif hasattr(self.retriever, "search"):
                result = self.retriever.search(question, top_k=top_k)
                for h in getattr(result, "hits", []):
                    policy_hits.append(
                        {
                            "control_id": h.control_id,
                            "score": h.score,
                            "section": h.metadata.get("section"),
                            "text": (h.text or "")[:200],
                        }
                    )

        notes = ""
        if paths and not control_ids:
            notes = (
                "Structural paths found, but no controls were linked to the "
                "involved nodes. Run link_controls_from_corpus() or add "
                "GOVERNED_BY edges."
            )
        elif not paths:
            notes = "No ExternalEntity → DataStore paths that cross a trust boundary were found."

        return GraphRAGAnswer(
            question=question,
            structural_findings=findings,
            policy_hits=policy_hits,
            notes=notes,
        )
