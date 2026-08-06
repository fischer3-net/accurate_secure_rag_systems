# Extra Credit Theory – DFD Fidelity, Canonical Models & RAG Implications

**Focus:** Understanding what is lost (and what is gained) when a visual Data Flow Diagram is turned into a structured JSON / graph representation, and how those losses affect every downstream RAG and evaluation step.

Welcome to the Extra Credit module. The core four weeks gave you a complete pipeline: high-quality chunking, hybrid + graph storage, modular skills, and automated evaluation. In real organizations one question keeps resurfacing:

> “We already have DFDs in Lucid, draw.io, Visio, or ThreatModeler. If we convert them to JSON so the RAG system can evaluate them, how much fidelity do we lose—and does it actually matter?”

This module answers that question with the same rigor we applied to retrieval and skills. Fidelity loss is real, but it is not uniform. Some losses are irrelevant (or even helpful). Others can silently break path queries, control matching, and the trustworthiness of the final compliance report.

---

## 1. Why a Structured Representation Is Necessary

A visual DFD is optimized for human consumption. A RAG-based compliance system needs a representation optimized for *machines*:

| Human visual DFD                          | Machine / RAG-ready model                          |
|-------------------------------------------|----------------------------------------------------|
| Spatial layout, colors, line styles       | Explicit nodes and typed edges                     |
| Implicit trust boundaries (dashed boxes)  | First-class `TrustBoundary` nodes + `CROSSES` edges |
| Free-text labels and notes                | Structured properties (classification, trust_level, protocol) |
| Ambiguous “DB1 → Service” arrows          | Directed `FLOWS_TO` edges with attributes          |

Without a canonical structured form, the skills you built in Week 3 (`check_trust_boundary_paths`, `match_security_controls`, `score_sdlc_compliance`) have nothing reliable to operate on. Graph path queries cannot run on pixels. Hybrid retrieval cannot filter on a property that exists only as a color.

The conversion step is therefore not optional—it is the bridge between the organization’s existing artifacts and the evaluation pipeline.

---

## 2. A Taxonomy of Fidelity Loss

Not all fidelity is equal. We distinguish four categories:

### 2.1 Visual / Layout Fidelity
Positions, sizes, alignment, colors, iconography, and decorative styling.

**Impact on RAG evaluation:** Almost zero.  
These elements rarely encode security-relevant facts. Losing them is usually beneficial because it removes noise.

### 2.2 Structural / Topological Fidelity
Which elements exist, how they connect, and which flows cross which trust boundaries.

**Impact on RAG evaluation:** High.  
Missing a trust boundary or an edge direction changes the answer to “Is there an unauthenticated path from External Entity X to Data Store Y?”. False negatives here are particularly dangerous in a compliance setting.

### 2.3 Semantic Fidelity
Attributes that give meaning to the topology: data classification, trust level of a process, authentication requirements on a flow, protocol, sensitivity of the data being moved.

**Impact on RAG evaluation:** High.  
A path may exist, but whether it *violates* a control often depends on these properties. If they are lost or left as free text, policy matching and scoring become incomplete or incorrect.

### 2.4 Provenance & Completeness Fidelity
Author, version, source tool, date, and any assumptions or notes that never became formal elements.

**Impact on RAG evaluation:** Medium to high for auditability.  
When a control decision is later challenged, “which version of the diagram was evaluated?” is a first-class question.

---

## 3. Implications for the RAG Pipeline

Fidelity problems do not stay confined to the conversion step. They propagate.

### 3.1 Retrieval (Weeks 1–2)
If the structured DFD lacks classification or trust-level properties, metadata pre-filters and hybrid queries cannot use them. The retriever may surface the wrong controls or fail to surface the right ones.

### 3.2 Graph-Augmented RAG (Lab 2.2)
Path queries are only as good as the graph. A missing `CROSSES` edge or an omitted TrustBoundary node produces both false negatives (“no violation found”) and false confidence.

### 3.3 Skills & Routing (Week 3)
- `validate_dfd_syntax` can catch many structural problems—if you give it a strict schema.
- `check_trust_boundary_paths` will silently miss violations when topology is incomplete.
- `match_security_controls` and `score_sdlc_compliance` inherit every upstream omission.

### 3.4 Evaluation & CI (Week 4)
Golden datasets and hit-rate / precision metrics become misleading if the input DFDs themselves are incomplete. You can achieve excellent scores on a flawed representation and still ship a system that fails on real diagrams.

### 3.5 Capstone & Production
The final ComplianceReport is only as trustworthy as the structured model that fed the skills. Auditability requires that the JSON (or graph) be treated as a controlled artifact, not a disposable export.

---

## 4. Design Patterns That Preserve What Matters

### 4.1 Canonical Schema First
Define a strict, versioned schema for DFD JSON (the course already uses a minimal version with `Process`, `DataStore`, `ExternalEntity`, `TrustBoundary` and typed edges). Make required security-relevant properties explicit rather than optional free text.

### 4.2 Validation as a First-Class Skill
The `validate_dfd_syntax` skill should do more than check that keys exist. It should enforce:

- Referential integrity of edges
- Presence of required properties for high-risk node types
- Explicit modeling of every trust-boundary crossing

### 4.3 Controlled Conversion, Not Blind Export
Prefer a conversion process that is:

- Tool-aware (different exporters lose different things)
- Reviewable (human or automated diff against the visual source for high-risk diagrams)
- Provenance-preserving (source tool, original file hash, converter version, operator)

### 4.4 Dual Representation Where Necessary
Keep the original visual artifact linked to the structured model. The visual remains the human-facing source of truth for discussion; the JSON/graph is the machine-facing source of truth for evaluation.

### 4.5 Progressive Enrichment
Start with topology. Add semantic properties in a second pass (classification, authentication, etc.). Do not require perfection on day one, but make incompleteness visible to the scoring skill.

---

## 5. Practical Decision Framework

```
Is the information only visual (layout, color, style)?
        │
        └─ YES → Accept the loss. Do not try to preserve it.

Is the information structural (nodes, edges, boundary crossings)?
        │
        └─ YES → Must be explicit in the JSON/graph. Validate strictly.

Is the information semantic (classification, trust level, authn, protocol)?
        │
        └─ YES → Prefer structured properties. If missing, surface the gap
                 in the compliance report rather than inventing values.

Is the information provenance or an author assumption?
        │
        └─ YES → Capture as metadata on the DfdDocument, not as a node.
```

---

## 6. Mapping to the Existing Course Artifacts

| Course component              | How fidelity issues appear                          | Mitigation already available / to extend |
|-------------------------------|-----------------------------------------------------|------------------------------------------|
| Week 1 chunking & metadata    | Controls retrieved without knowing data sensitivity | Richer metadata schema on DFD nodes      |
| Lab 2.2 Graph-Augmented RAG   | Missing paths or boundary crossings                 | Strict graph schema + validation         |
| Week 3 skills                 | Skills operate on incomplete inputs                 | Stronger `validate_dfd_syntax` + routing that refuses incomplete diagrams for high-risk routes |
| Week 4 evaluation             | Metrics computed on flawed fixtures                 | Include incomplete / lossy DFD fixtures in the golden set |
| Capstone                      | Final report trustworthiness                        | Require provenance + validation status in the ComplianceReport |

---

## 7. Recommended Python Building Blocks

The snippets below illustrate the patterns used in Labs EC.1 and EC.2. They deliberately build on the existing `graph_schema.py` from Lab 2.2 so you can drop them into the course codebase with minimal friction.

### 7.1 Canonical schema with required properties & provenance

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from datetime import datetime, timezone

ALLOWED_NODE_TYPES = {"Process", "DataStore", "ExternalEntity", "TrustBoundary"}
ALLOWED_EDGE_TYPES = {"FLOWS_TO", "CROSSES", "GOVERNED_BY"}

# Properties we treat as required for high-risk (full) evaluation
REQUIRED_NODE_PROPS = {
    "DataStore": {"classification", "trust_level"},
    "Process": {"trust_level"},
}
REQUIRED_EDGE_PROPS = {
    "FLOWS_TO": {"protocol"},  # authenticated / encrypted remain recommended
}

@dataclass
class Provenance:
    source_tool: str = "unknown"
    source_uri: str | None = None
    source_hash: str | None = None
    converter_version: str = "1.0.0"
    author: str | None = None
    converted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

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
    name: str
    nodes: list[DfdNode]
    edges: list[DfdEdge]
    description: str = ""
    provenance: Provenance = field(default_factory=Provenance)
    schema_version: str = "2026.1"
```

### 7.2 Fidelity validation – hard errors vs soft warnings

```python
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    severity: Literal["error", "warning"]
    code: str
    message: str
    node_or_edge_id: str | None = None

def validate_fidelity(doc: DfdDocument) -> list[ValidationIssue]:
    """Return structured issues. Errors block full evaluation; warnings reduce confidence."""
    issues: list[ValidationIssue] = []
    ids = {n.id for n in doc.nodes}

    # --- Structural integrity (hard errors) ---
    for e in doc.edges:
        if e.type in ("FLOWS_TO", "CROSSES"):
            if e.source not in ids:
                issues.append(ValidationIssue(
                    "error", "MISSING_SOURCE",
                    f"Edge source not found: {e.source}", e.source
                ))
            if e.target not in ids:
                issues.append(ValidationIssue(
                    "error", "MISSING_TARGET",
                    f"Edge target not found: {e.target}", e.target
                ))

    # --- Semantic completeness (soft warnings for high-risk evaluation) ---
    for n in doc.nodes:
        required = REQUIRED_NODE_PROPS.get(n.type, set())
        missing = required - n.properties.keys()
        for prop in missing:
            issues.append(ValidationIssue(
                "warning", "MISSING_NODE_PROP",
                f"{n.type} '{n.id}' is missing required property '{prop}'",
                n.id
            ))

    for e in doc.edges:
        required = REQUIRED_EDGE_PROPS.get(e.type, set())
        missing = required - e.properties.keys()
        for prop in missing:
            issues.append(ValidationIssue(
                "warning", "MISSING_EDGE_PROP",
                f"Edge {e.source}->{e.target} missing '{prop}'",
                f"{e.source}->{e.target}"
            ))

    return issues


def has_blocking_errors(issues: list[ValidationIssue]) -> bool:
    return any(i.severity == "error" for i in issues)
```

### 7.3 Controlled conversion with provenance

```python
import hashlib
import json
from pathlib import Path

def convert_with_provenance(
    raw: dict,
    *,
    source_tool: str,
    source_uri: str | None = None,
    author: str | None = None,
    converter_version: str = "1.0.0",
) -> DfdDocument:
    """Turn a raw export (or hand-authored dict) into a provenance-aware DfdDocument."""
    payload = json.dumps(raw, sort_keys=True, ensure_ascii=False).encode()
    source_hash = hashlib.sha256(payload).hexdigest()[:16]

    nodes = [DfdNode(**n) for n in raw["nodes"]]
    edges = [DfdEdge(**e) for e in raw["edges"]]

    return DfdDocument(
        name=raw.get("name", "unnamed"),
        description=raw.get("description", ""),
        nodes=nodes,
        edges=edges,
        provenance=Provenance(
            source_tool=source_tool,
            source_uri=source_uri,
            source_hash=source_hash,
            converter_version=converter_version,
            author=author,
        ),
    )
```

### 7.4 Minimal impact-measurement harness (Lab EC.2 sketch)

```python
from typing import Callable

def run_fidelity_ablation(
    complete_doc: DfdDocument,
    lossy_doc: DfdDocument,
    path_query_fn: Callable,
    retrieve_controls_fn: Callable,
    question: str,
) -> dict:
    """Compare path-query and retrieval results on complete vs lossy models."""
    complete_paths = path_query_fn(complete_doc)
    lossy_paths = path_query_fn(lossy_doc)

    complete_controls = retrieve_controls_fn(complete_doc, question)
    lossy_controls = retrieve_controls_fn(lossy_doc, question)

    return {
        "path_query": {
            "complete_found_violation": bool(complete_paths),
            "lossy_found_violation": bool(lossy_paths),
            "false_negative": bool(complete_paths) and not bool(lossy_paths),
        },
        "retrieval": {
            "complete_control_ids": sorted(c["control_id"] for c in complete_controls),
            "lossy_control_ids": sorted(c["control_id"] for c in lossy_controls),
        },
        "validation": {
            "complete_issues": validate_fidelity(complete_doc),
            "lossy_issues": validate_fidelity(lossy_doc),
        },
    }
```

These building blocks keep the conversion step explicit, make incompleteness observable, and give you a concrete way to measure how much fidelity loss changes the answers your RAG pipeline produces.

---

## Key Takeaways

- Visual fidelity loss is rarely a problem for RAG-based compliance evaluation; structural and semantic fidelity loss are real and consequential.
- The conversion from visual DFD to structured JSON/graph is a first-class design decision, not a mechanical export step.
- Every downstream component (retrieval, graph queries, skills, evaluation metrics, final report) inherits the quality of that structured model.
- Treat the JSON representation as a controlled artifact: versioned, validated, and linked back to its visual source.
- Explicitly surface incompleteness rather than silently inventing or ignoring missing attributes.

**Next:** Lab EC.1 turns these principles into a concrete canonical schema and validation skill. Lab EC.2 measures how different degrees of fidelity loss change the answers produced by the existing RAG and skill pipeline.

---

## Addendum: Mathematical & Formal Foundations

### A.1 Completeness of a Structured DFD

Let \(D_v\) be the visual diagram and \(D_s\) its structured representation.  
Define a set of security-relevant predicates \(P = \{p_1, p_2, \dots, p_m\}\) (e.g., “flow \(f\) crosses trust boundary \(b\)”, “data store \(s\) has classification confidential”).

The **structural completeness** of \(D_s\) relative to \(D_v\) can be expressed as:

\[
C_{\text{struct}}(D_s, D_v) = \frac{|\{p \in P_{\text{struct}} : p(D_s) = p(D_v)\}|}{|P_{\text{struct}}|}
\]

where \(P_{\text{struct}}\) is the subset of predicates that are topological.

Semantic completeness is defined analogously over \(P_{\text{sem}}\).

### A.2 Impact on Path-Based Evaluation

A trust-boundary violation query is essentially an existence check:

\[
\exists \text{ path } \pi : \text{ExternalEntity} \leadsto \text{DataStore}
\quad\text{such that}\quad
\pi \text{ crosses a TrustBoundary} \land \text{authn}(\pi) = \text{false}
\]

If any required edge or node is missing from \(D_s\), the existential quantifier evaluates to false even when the visual diagram contains the violation. This is a **false negative** whose probability grows with the incompleteness of the model.

### A.3 Propagation into Retrieval Precision

When downstream retrieval uses properties of \(D_s\) as filters or as part of the query text, missing attributes reduce the effective signal available to both the sparse and dense retrievers. In the limit, the hybrid score

\[
\text{score}_{\text{hybrid}}(d) = \alpha \cdot \text{sim}_{\text{dense}}(q, d) + (1-\alpha) \cdot \text{sim}_{\text{sparse}}(q, d)
\]

is computed against an impoverished query \(q\) derived from an incomplete \(D_s\), lowering both precision and recall of the governing controls.

### A.4 Validation as a Guard

Let \(V(D_s)\) be a validation function that returns a set of errors. A practical policy for high-risk routes is:

\[
\text{if } V(D_s) \neq \emptyset \text{ then refuse full evaluation route}
\]

This converts silent fidelity loss into an explicit, auditable failure—preferable in a compliance context.
