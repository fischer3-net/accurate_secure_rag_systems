# Week 1 Theory – Precision RAG & Domain Chunking

!!! note "Status"
    Skeleton page. Expand with full lecture content, diagrams, and references.

## 1. The Multi-Document Alignment Problem

Why standard naive RAG fails when evaluating complex DFDs against SDLC handbooks and technical security baselines.

- Hierarchy mismatch: Section-level policy requirements vs. component-level diagram elements.
- Cross-document entity resolution and trust-boundary mapping.

## 2. Advanced Chunking Strategies in Python

- Beyond fixed-size chunking: Document-aware splitting (AST / Markdown / JSON / XML parsing).
- Parent-Child and Small-to-Big retrieval paradigms for dense security standards.
- Semantic chunking and metadata enrichment (tagging chunks with asset types, risk tiers, SDLC phases).

### Recommended Libraries

```python
# Example imports (to be expanded)
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
# Custom AST-based splitters for structured policy documents
```

## 3. Hybrid Retrieval Architecture

- Combining Dense Vector Embeddings (Vertex AI Embeddings) with Sparse Keyword Search (BM25).
- Reciprocal Rank Fusion (RRF) and re-ranking models (Vertex AI Ranking API) to boost top-k precision.

## Next Steps

Proceed to the hands-on labs:

- [Lab 1.1](lab-1.1.md)
- [Lab 1.2](lab-1.2.md)
