# Lab 01 – Chunking & Metadata Enrichment

This directory contains the starter materials and student implementations for **Lab 1.1**.

## Expected Layout

```
01-chunking/
├── README.md                 # This file
├── data/                     # Source policy documents (Markdown preferred)
│   ├── sdlc_handbook.md      # SDLC handbook or relevant excerpt
│   └── security_baseline.md  # Technical security baseline / controls
├── src/                      # Production-style Python modules (recommended)
│   ├── chunking.py
│   ├── metadata.py
│   └── ingest.py
├── notebooks/
│   └── lab-1.1-chunking.ipynb
└── tests/                    # Optional but encouraged
    └── test_chunking.py
```

## Quick Start for Students

1. Place or create the two source Markdown documents in `data/`.
2. Implement document-aware splitting + Parent-Child logic + metadata enrichment.
3. Write the enriched records to BigQuery (and/or prepare them for Vertex AI Vector Search).
4. Run the validation checklist described in the lab guide.
5. Submit via Moodle.

See the full instructions:

**[Lab 1.1 – Document-Aware Chunking & Metadata Enrichment](../../docs/week-01/lab-1.1.md)**

## Sample Document Guidance

If your organisation cannot share real handbooks, create realistic synthetic Markdown documents that contain:

- Hierarchical headings (H1–H3)
- Numbered security controls related to data flows, trust boundaries, external entities, and data stores
- Explicit mentions of SDLC phases / gates

The quality of the source documents directly affects the quality of the retrieval corpus used in all later labs and the Capstone.
