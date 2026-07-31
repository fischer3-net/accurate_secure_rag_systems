# Lab 2.2 – Graph-Augmented RAG for DFD Connectivity

**Objective:** Model a Data Flow Diagram as a graph, link its elements to the policy chunks from Week 1, and answer structural compliance questions that pure vector search cannot.

---

## Learning Goals

- Define a minimal but useful DFD graph schema (Process, DataStore, ExternalEntity, DataFlow, TrustBoundary).
- Ingest a sample DFD and connect nodes to relevant `control_id`s / chunk IDs.
- Implement a hybrid query: graph traversal first, then semantic (or hybrid) retrieval over the linked policy text.
- Demonstrate at least one structural violation that vector-only search misses.

---

## Why Graph RAG here?

Consider the question:

> “Is there an unauthenticated path from External Entity *Partner API* to Data Store *Customer PII* that crosses a trust boundary?”

A pure vector search over policy text may retrieve the right *controls*, but it cannot tell you whether the *diagram under review* actually contains that path. Graph traversal answers the structural half; vector / hybrid retrieval then supplies the governing controls and risk language.

---

## Starter Location

```
labs/02-storage/
├── src/
│   ├── graph_schema.py        # node / edge types + validation
│   ├── graph_store.py         # in-memory graph (NetworkX-style pure Python)
│   └── graph_rag.py           # hybrid: expand subgraph → retrieve policies
├── data/
│   └── sample_dfd.json        # small but realistic DFD with a hidden violation
├── notebooks/
│   └── lab-2.2-graph-rag.ipynb
└── tests/
    └── test_graph_rag.py
```

An optional Neo4j driver path is sketched in comments so you can point the same interface at Aura or a GKE-hosted instance later.

---

## DFD Graph Schema (minimal)

**Nodes**

| Label | Key properties |
|-------|----------------|
| `Process` | id, name, trust_level |
| `DataStore` | id, name, classification, trust_level |
| `ExternalEntity` | id, name |
| `TrustBoundary` | id, name |

**Edges**

| Type | Meaning |
|------|---------|
| `FLOWS_TO` | Data flow from source → target (Process/DataStore/ExternalEntity) |
| `CROSSES` | A `FLOWS_TO` edge that crosses a TrustBoundary |
| `GOVERNED_BY` | Element or flow → policy `control_id` / chunk_id |

---

## Step-by-Step

### 1. Load the sample DFD

```python
from src.graph_store import DfdGraphStore
from src.graph_schema import load_dfd_json

g = DfdGraphStore()
g.ingest(load_dfd_json("data/sample_dfd.json"))
print(g.summary())
```

### 2. Link controls from the Week 1 corpus

```python
g.link_controls_from_corpus(corpus)   # matches asset_type / keywords → GOVERNED_BY
```

### 3. Structural query

```python
paths = g.find_paths(
    source_type="ExternalEntity",
    target_type="DataStore",
    require_crosses_trust_boundary=True,
)
for p in paths:
    print(p)
```

### 4. Graph-Augmented retrieval

```python
from src.graph_rag import GraphRAG

grag = GraphRAG(graph=g, retriever=hybrid_retriever_from_week1)
answer = grag.ask(
    "Are there unauthenticated flows from external entities to PII stores?"
)
# answer contains: structural findings + ranked policy chunks
```

### 5. Contrast with pure vector search

Show one query where the graph path surfaces a violation that the pure vector top-k does not mention (because the violation is in the *diagram topology*, not in the policy wording).

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Sample DFD loads and produces a non-empty graph | Yes |
| At least one path that crosses a trust boundary is discovered | Yes |
| Graph-Augmented query returns both structural findings and policy chunks | Yes |
| Notebook documents a case pure vector search misses | Yes |
| Unit tests cover schema validation and path finding | Yes |

---

## Submission

1. Completed notebook with structural findings + policy citations.
2. Short note on how you would persist the graph in Neo4j or Spanner Graph for production.
3. Link or PR via Moodle.

**Next:** Week 3 turns the retrieval + storage stack into modular, least-privilege *skills* that an agent can call without prompt bloat.
