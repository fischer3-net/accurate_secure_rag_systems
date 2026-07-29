# Lab 1.1 – Parsing and Metadata-Enriching SDLC & Security Documents

**Objective:** Ingest an SDLC handbook and a security requirements document into a structured representation suitable for Vertex AI Vector Search / BigQuery, with rich domain metadata.

## Deliverables

- Python script or notebook that:
  1. Parses the source documents (Markdown / PDF / structured text).
  2. Applies document-aware chunking.
  3. Attaches metadata: `doc_type`, `section`, `asset_type`, `risk_tier`, `sdlc_phase`, `source_uri`.
  4. Writes enriched chunks to BigQuery and/or prepares them for Vertex AI Vector Search indexing.

## Starter Location

Code skeleton lives in the repository:

```
labs/01-chunking/
notebooks/lab-1.1-chunking.ipynb   # (to be added)
```

## Success Criteria

- Chunks respect logical document boundaries (no mid-sentence or mid-control splits).
- Metadata is queryable and improves retrieval precision in later labs.
- Pipeline is idempotent and can be re-run safely.

## Instructions

1. Clone / open the lab directory.
2. Review the provided sample documents.
3. Implement the chunking + enrichment logic.
4. Validate with a small retrieval smoke test.
5. Submit notebook / PR link via Moodle assignment.

!!! tip
    Prefer Parent-Child indexing so that small precise chunks can still surface the larger surrounding policy context.
