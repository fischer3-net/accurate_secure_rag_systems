# Lab 2.1 – Hybrid Store Benchmark: AlloyDB-style vs Vector-Search-style

**Objective:** Implement two retrieval backends that share the same interface, load the Week 1 enriched corpus into both, and measure quality + latency so you can make an evidence-based storage recommendation for the DFD compliance use case.

---

## Learning Goals

- Map the `ChunkRecord` schema onto a relational + vector table (AlloyDB / pgvector pattern) and onto a pure vector index (Vertex AI Vector Search pattern).
- Run identical evaluation queries against both backends.
- Record precision / hit-rate and simple latency statistics.
- Write a short recommendation that links the numbers back to the trade-off matrix in the theory page.

---

## Why two “styles” instead of live AlloyDB + Matching Engine?

Provisioning real AlloyDB and Vertex AI Vector Search indexes is valuable in a production project, but it is heavy for a workshop (billing, IAM, VPC, index build time).  

This lab therefore provides:

| Backend | What it simulates | Runs offline? |
|---------|-------------------|---------------|
| `PgVectorStore` | AlloyDB / Cloud SQL + pgvector hybrid SQL + vector | Yes (in-memory / SQLite-style) |
| `VectorSearchStore` | Vertex AI Vector Search pure ANN + optional restrict | Yes (in-memory dense index) |
| Optional live clients | Real AlloyDB or Vertex AI when credentials exist | When you enable them |

The **interface** is what matters for the Capstone: your skills and evaluation suite should depend on a storage abstraction, not on a concrete product.

---

## Starter Location

```
labs/02-storage/
├── src/
│   ├── store_base.py          # common interface + ChunkRecord adapter
│   ├── pgvector_store.py      # hybrid filter + vector (AlloyDB-style)
│   ├── vector_search_store.py # pure semantic (Vector Search-style)
│   └── benchmark.py           # shared evaluation + latency harness
├── notebooks/
│   └── lab-2.1-benchmark.ipynb
├── scripts/
│   ├── provision_alloydb.md
│   └── provision_vector_search.md
├── data/                      # re-uses Week 1 corpus via relative path
└── tests/
    └── test_stores.py
```

---

## Step-by-Step

### 1. Load the Week 1 corpus

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path("../../01-chunking").resolve()))

from src.chunking import process_directory
from src.ingest import write_jsonl

corpus = process_directory(Path("../../01-chunking/data"))
write_jsonl(corpus, "output/rag_chunks.jsonl")
```

### 2. Index into both stores

```python
from src.pgvector_store import PgVectorStore
from src.vector_search_store import VectorSearchStore

pg = PgVectorStore()
pg.upsert(corpus)

vs = VectorSearchStore()
vs.upsert(corpus)
```

### 3. Run the same queries

```python
from src.benchmark import run_benchmark
from src.retrieval_adapter import load_eval_queries  # or from week-1 package

results = run_benchmark(
    stores={"pgvector": pg, "vector_search": vs},
    queries=load_eval_queries(...),
    k=3,
)
print(results.summary())
```

### 4. Interpret and recommend

Fill in the short recommendation section in the notebook:

- Which backend won on hit-rate@3 for *filtered* queries (asset_type / risk_tier)?
- Which was faster for pure semantic queries?
- For the Capstone interactive DFD reviewer, which would you choose first and why?

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Both stores implement the same `upsert` / `search` interface | Yes |
| Benchmark runs offline without GCP credentials | Yes |
| Hit-rate@3 reported for both backends on the Week 1 query set | Yes |
| Short written recommendation present in the notebook | Yes |
| Optional live AlloyDB / Vertex paths documented | Yes |

---

## Provisioning (optional, production path)

See:

- `scripts/provision_alloydb.md` – AlloyDB Omni / Cloud SQL + pgvector sketch
- `scripts/provision_vector_search.md` – Vertex AI Vector Search index creation sketch

You do **not** need live resources to complete the lab or the Capstone prototype.

---

## Submission

1. Completed notebook with benchmark table and recommendation paragraph.
2. Any extensions (e.g. real AlloyDB connection string under a feature flag).
3. Link or PR via Moodle.

**Next:** Lab 2.2 adds a graph layer so structural DFD questions can be answered alongside semantic policy lookup.
