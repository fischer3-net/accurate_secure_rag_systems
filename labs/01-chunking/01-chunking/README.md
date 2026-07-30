# Lab 01 – Chunking & Metadata Enrichment

This directory contains the **starter implementation** and student workspace for **Lab 1.1**.

## Layout

```
01-chunking/
├── README.md                 # This file
├── data/                     # Source policy documents
│   ├── sdlc_handbook.md
│   └── security_baseline.md
├── src/                      # Production-style reference implementation
│   ├── __init__.py
│   ├── chunking.py           # Document-aware split + Parent-Child
│   ├── metadata.py           # Pydantic schema + deterministic enrichment
│   └── ingest.py             # BigQuery + JSONL writers
├── notebooks/
│   └── lab-1.1-chunking.ipynb
├── tests/
│   └── test_chunking.py
├── requirements.txt
└── output/                   # Generated corpus (git-ignored)
    └── rag_chunks.jsonl
```

## Quick Start

```bash
# From the labs/01-chunking directory
pip install -r requirements.txt   # or the packages listed in the lab guide

# Run the unit tests (offline, no GCP required)
pytest tests/ -v

# Explore interactively
jupyter notebook notebooks/lab-1.1-chunking.ipynb
```

### One-liner to build the corpus

```python
from src.chunking import process_directory
from src.ingest import write_jsonl

corpus = process_directory("data")
write_jsonl(corpus, "output/rag_chunks.jsonl")
print(f"Wrote {len(corpus)} enriched chunks")
```

## What the starter already provides

| Component | Status |
|-----------|--------|
| MarkdownHeaderTextSplitter (heading-aware) | ✅ |
| Parent-Child (section strategy) | ✅ |
| Full compliance metadata schema (Pydantic) | ✅ |
| Deterministic enrichment rules (control_id, asset_type, risk_tier, sdlc_phase) | ✅ |
| JSONL writer + round-trip loader | ✅ |
| BigQuery writer (optional, needs credentials) | ✅ |
| Validation helpers | ✅ |
| Unit tests | ✅ |
| Guided notebook | ✅ |

Students are expected to:

1. Run and understand the reference pipeline.
2. Experiment with alternative parent strategies or enrichment rules.
3. Optionally extend the pipeline to PDF sources or additional metadata fields.
4. Persist the corpus (JSONL and/or BigQuery) for use in Lab 1.2.

## Full instructions

See the lab guide:

**[Lab 1.1 – Document-Aware Chunking & Metadata Enrichment](../../docs/week-01/lab-1.1.md)**

## Sample Document Guidance

If your organisation cannot share real handbooks, the provided synthetic documents already contain:

- Hierarchical headings (H1–H3)
- Numbered security controls related to data flows, trust boundaries, external entities, and data stores
- Explicit Risk Tier and SDLC Phase annotations

You may replace them with anonymised excerpts from your own environment; the pipeline will adapt as long as the Markdown structure is preserved.
