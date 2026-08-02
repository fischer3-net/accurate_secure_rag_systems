# Lab 01 – Chunking, Metadata & Hybrid Retrieval

This directory contains the **starter implementation** for **Lab 1.1** and **Lab 1.2**.

## Layout

```
01-chunking/
├── README.md
├── data/
│   ├── sdlc_handbook.md
│   ├── security_baseline.md
│   └── evaluation_queries.json      # Lab 1.2 ground-truth queries
├── src/
│   ├── __init__.py
│   ├── chunking.py                  # Lab 1.1 – document-aware split + Parent-Child
│   ├── metadata.py                  # Lab 1.1 – Pydantic schema + enrichment
│   ├── ingest.py                    # Lab 1.1 – BigQuery + JSONL
│   └── retrieval.py                 # Lab 1.2 – BM25, dense, RRF, re-ranker, eval
├── notebooks/
│   ├── lab-1.1-chunking.ipynb
│   └── lab-1.2-hybrid-rerank.ipynb
├── tests/
│   ├── test_chunking.py
│   └── test_retrieval.py
├── requirements.txt
└── output/                          # Generated corpus (git-ignored)
    └── rag_chunks.jsonl
```

## Quick Start

```bash
# From the labs/01-chunking directory
pip install -r requirements.txt

# Run all unit tests (offline, no GCP required)
pytest tests/ -v

# Lab 1.1 notebook
jupyter notebook notebooks/lab-1.1-chunking.ipynb

# Lab 1.2 notebook
jupyter notebook notebooks/lab-1.2-hybrid-rerank.ipynb
```

### Build corpus + run hybrid retrieval in a few lines

```python
from src.chunking import process_directory
from src.ingest import write_jsonl
from src.retrieval import HybridRetriever, HashingEmbedder, load_eval_queries, evaluate_retriever

corpus = process_directory("data")
write_jsonl(corpus, "output/rag_chunks.jsonl")

retriever = HybridRetriever.from_jsonl("output/rag_chunks.jsonl", embedder=HashingEmbedder())
result = retriever.retrieve("Can an external entity write directly to a data store?", top_k=3)
for h in result.final_hits:
    print(h.rank, h.control_id, h.score)

queries = load_eval_queries("data/evaluation_queries.json")
metrics = evaluate_retriever(retriever, queries, k=3)
print("Hit-rate@3:", metrics["mean_hit_rate_at_3"])
```

## What is provided

| Component | Lab | Status |
|-----------|-----|--------|
| Document-aware Markdown splitting | 1.1 | ✅ |
| Parent-Child chunk construction | 1.1 | ✅ |
| Compliance metadata schema + deterministic enrichment | 1.1 | ✅ |
| JSONL + BigQuery writers | 1.1 | ✅ |
| BM25 sparse index (pure Python) | 1.2 | ✅ |
| Dense index (HashingEmbedder offline / VertexEmbedder) | 1.2 | ✅ |
| Reciprocal Rank Fusion | 1.2 | ✅ |
| Lightweight domain re-ranker | 1.2 | ✅ |
| Metadata pre-filters | 1.2 | ✅ |
| Evaluation harness (precision@k + hit-rate@k) | 1.2 | ✅ |
| Guided notebooks + unit tests | both | ✅ |

## Full instructions

- [Lab 1.1 – Document-Aware Chunking & Metadata](../../docs/week-01/lab-1.1.md)
- [Lab 1.2 – Hybrid Retrieval + Re-ranking](../../docs/week-01/lab-1.2.md)
