# Lab 1.1 – Document-Aware Chunking & Metadata Enrichment

**Objective:** Build a reproducible Python pipeline that ingests an SDLC handbook and a technical security baseline, applies document-aware chunking, attaches rich domain metadata, and prepares the resulting corpus for Vertex AI Vector Search and/or BigQuery.

This lab produces the high-quality retrieval foundation used by every subsequent module and the Capstone.

---

## Learning Goals

By completing this lab you will be able to:

- Parse Markdown (and optionally PDF) policy documents while preserving heading hierarchy.
- Implement Parent-Child (Small-to-Big) chunking so that precise controls retain their surrounding context.
- Attach a consistent compliance-oriented metadata schema.
- Write the enriched chunks to a queryable store (BigQuery recommended for inspection; Vertex AI Vector Search index preparation for later labs).
- Validate that chunk boundaries and metadata are correct before moving to hybrid retrieval.

---

## Prerequisites

- GCP project with the following APIs enabled:
  - Vertex AI API
  - BigQuery API
- Python 3.11+ environment (Cloud Shell, Vertex AI Workbench, or local with Application Default Credentials)
- Basic familiarity with the Vertex AI SDK and BigQuery client libraries

Install the core packages if needed:

```bash
pip install google-cloud-aiplatform google-cloud-bigquery langchain-text-splitters langchain-core python-dotenv
```

---

## Recommended Metadata Schema

Every chunk produced by this lab **must** carry at least the following fields:

| Field | Type | Description / Example Values |
|-------|------|------------------------------|
| `chunk_id` | string (UUID) | Unique identifier |
| `doc_type` | string | `sdlc_handbook`, `security_baseline` |
| `section` | string | Full hierarchical path, e.g. `"3.2 Architecture Review Gate"` |
| `control_id` | string \| null | e.g. `"SEC-DFD-014"` if present |
| `asset_type` | string | `process`, `data_store`, `external_entity`, `trust_boundary`, `data_flow`, `general` |
| `risk_tier` | string | `critical`, `high`, `medium`, `low`, `unspecified` |
| `sdlc_phase` | string | `requirements`, `design`, `implementation`, `verification`, `maintenance`, `general` |
| `source_uri` | string | Path or GCS URI of the original document |
| `parent_id` | string \| null | ID of the parent chunk (for Parent-Child) |
| `chunk_type` | string | `child`, `parent`, `standalone` |
| `text` | string | The actual chunk content |
| `token_count` | int | Approximate token length (optional but useful) |

You may extend the schema, but do not remove these core fields — later labs and the Capstone evaluation suite expect them.

---

## Lab Structure & Starter Location

```
labs/01-chunking/
├── README.md
├── data/                     # Place sample SDLC handbook + security baseline here
│   ├── sdlc_handbook.md
│   └── security_baseline.md
├── src/
│   ├── chunking.py           # Core splitting + enrichment logic
│   ├── metadata.py           # Schema helpers and validation
│   └── ingest.py             # BigQuery / Vector Search writers
├── notebooks/
│   └── lab-1.1-chunking.ipynb
└── tests/
    └── test_chunking.py      # Optional but recommended
```

A complete reference implementation is already present under `labs/01-chunking/src/`, together with a guided notebook and unit tests. Sample policy documents live in `data/`. You may replace the samples with your organisation’s anonymised excerpts; the pipeline will adapt as long as the Markdown heading structure is preserved.

---

## Step-by-Step Instructions

### 1. Prepare the source documents

Place at least two Markdown documents in `labs/01-chunking/data/`:

- One SDLC handbook (or relevant excerpt) containing hierarchical sections and gates.
- One technical security baseline containing numbered controls related to data flows, trust boundaries, external entities, and data stores.

### 2. Document-aware splitting (already implemented in `src/chunking.py`)

The starter uses `MarkdownHeaderTextSplitter` so that chunks respect heading boundaries. Study the implementation, then experiment with your own variations.

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,   # keep headers in the text for context
)
```

### 3. Create Parent-Child pairs (recommended)

For dense control sections:

- Treat each leaf control (or small logical unit) as a **child**.
- Create a **parent** chunk that contains the surrounding section text or a summary of related controls.
- Link them via `parent_id` / `chunk_type`.

This pattern dramatically improves both precision and the ability of the LLM to ground its answers.

### 4. Enrich with domain metadata

Write a function that inspects the section path, control identifiers, and keywords to populate `asset_type`, `risk_tier`, `sdlc_phase`, etc. Prefer deterministic rules over LLM-based classification for this foundational lab (you can add LLM enrichment later).

### 5. Persist the corpus

Two recommended paths (implement at least one):

**A. BigQuery (excellent for inspection and later SQL + vector hybrid queries)**

```python
from google.cloud import bigquery

# Create a table with the schema above and load the enriched records.
```

**B. Prepare for Vertex AI Vector Search**

Write a JSONL or use the Vertex AI SDK to create an index with the text + metadata. You do not need a fully deployed Matching Engine index yet — preparing the documents is sufficient for this lab.

### 6. Validation checklist

Before considering the lab complete, verify:

- [ ] No chunk is split mid-sentence or mid-control.
- [ ] Every chunk has a complete metadata record (no missing required fields).
- [ ] Parent-Child relationships are correctly linked.
- [ ] A simple smoke test (embed a few queries and retrieve) returns relevant controls with correct metadata filters.
- [ ] The pipeline is idempotent (re-running does not create duplicates).

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Logical boundaries respected | 100 % of sampled chunks |
| Required metadata present | 100 % of chunks |
| Parent-Child linkage (if used) | Correct and bidirectional |
| Reproducibility | Same input → same chunk set |
| Usable by later labs | Corpus can be loaded by Lab 1.2 and Capstone |

---

## Submission

1. Push your completed code and notebook to a branch or fork of the course repository.
2. Submit the GitHub link (or PR) via the Moodle Lab 1.1 assignment activity.
3. Include a short note (in the notebook or a `NOTES.md`) describing any design decisions or deviations from the recommended schema.

---

## Tips for Security-Focused Practitioners

- Prefer deterministic metadata rules for controls that carry regulatory weight.
- Keep an audit trail of which source document and section produced each chunk.
- Treat the original policy documents as immutable; the enriched corpus is a derived artefact.
- When in doubt about chunk size, err on the side of slightly smaller children + rich parents rather than large monolithic blocks.

**Next Lab:** [Lab 1.2 – Hybrid Retrieval + Re-ranking](lab-1.2.md) will consume the corpus you just built.
