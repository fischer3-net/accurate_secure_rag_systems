# Week 1 – Precision RAG Management & Domain Chunking for Compliance Data

**Focus:** Tackling inaccuracy, hallucination, and naive retrieval limitations when cross-referencing DFDs with multi-source policies.

## Learning Outcomes

By the end of this week you will be able to:

- Explain why standard naive RAG fails on multi-document alignment tasks (DFDs ↔ SDLC handbooks ↔ security baselines).
- Implement document-aware chunking (AST / Markdown / JSON / XML) and Parent-Child / Small-to-Big retrieval patterns.
- Enrich chunks with domain metadata (asset type, risk tier, SDLC phase).
- Build a hybrid retrieval pipeline (Dense Vector + BM25 + Reciprocal Rank Fusion + Vertex AI Ranking).

## Agenda

1. Theory – Multi-document alignment problem & advanced chunking strategies
2. Lab 1.1 – Parsing and metadata-enriching an SDLC handbook + security requirements document
3. Lab 1.2 – Custom Python re-ranker pipeline that improves top-3 retrieval precision

## Prerequisites for Labs

- GCP project with Vertex AI API enabled
- Python 3.11+ environment (Cloud Shell, Colab, or local with `google-cloud-aiplatform`)
- Access to sample DFD / policy documents (provided in `/labs/01-chunking`)

## Navigation

- [Theory](theory.md)
- [Lab 1.1 – Document-aware Chunking & Metadata](lab-1.1.md)
- [Lab 1.2 – Hybrid Retrieval + Re-ranking](lab-1.2.md)
