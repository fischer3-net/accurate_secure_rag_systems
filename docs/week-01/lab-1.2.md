# Lab 1.2 – Hybrid Retrieval + Custom Re-ranker Pipeline

**Objective:** Implement a hybrid retrieval stack (dense + sparse) with Reciprocal Rank Fusion and a re-ranking stage that measurably improves top-3 precision for DFD security policy checks.

## Deliverables

- Working hybrid retriever that combines:
  - Vertex AI Embeddings (`text-embedding-004` or later)
  - BM25 / keyword search
  - RRF fusion
  - Optional Vertex AI Ranking API or a lightweight cross-encoder re-ranker
- Evaluation notebook showing precision@3 / recall@k improvement versus pure vector search baseline.

## Starter Location

```
labs/01-chunking/
notebooks/lab-1.2-hybrid-rerank.ipynb
```

## Success Criteria

- Demonstrable lift in top-3 precision on a held-out set of DFD-related queries.
- Clean, documented Python code that can be reused in later modules and the capstone.

## Key Concepts to Apply

- Reciprocal Rank Fusion formula
- Metadata filtering before or after fusion
- Latency vs. accuracy trade-offs of re-ranking
