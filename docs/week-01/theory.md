# Week 1 Theory – Precision RAG & Domain Chunking for Compliance Data

**Focus:** Why naive RAG fails on multi-document compliance tasks and how to design chunking + metadata strategies that preserve hierarchical and cross-document relationships.

---

## 1. The Multi-Document Alignment Problem

Security and architecture teams increasingly want to ask questions such as:

> “Does this Data Flow Diagram violate any controls in our SDLC handbook or the technical security baseline regarding trust boundaries and external entity access?”

This is a classic **multi-document alignment** problem. The system must simultaneously reason over:

| Document Type | Typical Structure | Granularity of Interest |
|---------------|-------------------|--------------------------|
| Data Flow Diagram (DFD) | Processes, Data Stores, External Entities, Data Flows, Trust Boundaries | Component / edge level |
| SDLC Handbook | Hierarchical sections, gates, phase requirements | Section / control level |
| Technical Security Baseline | Numbered controls, risk statements, implementation guidance | Individual control or sub-control |

### Why standard “naive RAG” fails here

1. **Hierarchy mismatch**  
   A fixed-size or pure semantic chunk from the SDLC handbook may contain only a partial control statement. The corresponding DFD element may need the parent section context (e.g., “Phase 3 – Architecture Review Gate”) to be correctly evaluated.

2. **Cross-document entity resolution**  
   Terms such as “External Entity”, “Trust Boundary”, “Data Store”, or specific asset names appear in both the diagram and the policy documents, but with different surrounding language. Pure vector similarity often retrieves the wrong sense of the term.

3. **Loss of structural relationships**  
   Security evaluation frequently depends on connectivity (Process → Data Store → External Entity) and on whether a flow crosses a trust boundary. Flat chunks destroy this graph-like information.

4. **Hallucination under sparse retrieval**  
   When the top-k retrieved chunks do not contain the exact control language, the LLM tends to invent plausible but non-grounded compliance statements — unacceptable in a security context.

**Goal of this week:** Build a retrieval foundation that preserves hierarchy, enriches domain metadata, and surfaces the right policy context for any given DFD element or flow.

---

## 2. Advanced Chunking Strategies in Python

### 2.1 Beyond Fixed-Size Chunking

Fixed-size (or even recursive character) splitters are convenient but destroy the logical units that matter for compliance:

- A security control should rarely be split mid-sentence.
- A Markdown heading hierarchy in an SDLC handbook is a strong signal of semantic boundaries.
- JSON/XML representations of DFDs have explicit element boundaries that should be respected.

**Preferred approaches for this course:**

| Strategy | When to use | Library / Technique |
|----------|-------------|---------------------|
| Markdown header-aware | SDLC handbooks, security baselines written in Markdown | `MarkdownHeaderTextSplitter` |
| Document-structure aware | Structured policy (JSON, XML, YAML) | Custom recursive split on keys / tags |
| Parent-Child (Small-to-Big) | Dense control catalogues | Store small precise chunks + larger parent context |
| Semantic chunking | Long narrative sections | Embedding-based boundary detection (use sparingly) |

### 2.2 Parent-Child / Small-to-Big Retrieval

This pattern is particularly powerful for security standards:

- **Child chunks** are small, precise units (individual controls or sub-requirements) that can be matched accurately via vector search.
- **Parent chunks** contain the surrounding section, rationale, or related controls.
- At retrieval time you return the child (for precision) **and** the parent (for context), or you expand the parent after the child is selected.

This avoids the classic trade-off between “too small → loses meaning” and “too large → dilutes relevance.”

### 2.3 Metadata Enrichment (Critical for Compliance)

Raw text chunks are rarely enough. For DFD security evaluation we recommend a consistent metadata schema:

```python
{
    "doc_type": "sdlc_handbook" | "security_baseline" | "dfd",
    "section": "3.2 Architecture Review Gate",
    "control_id": "SEC-DFD-014",          # if present
    "asset_type": "data_store" | "process" | "external_entity" | "trust_boundary" | "general",
    "risk_tier": "critical" | "high" | "medium" | "low",
    "sdlc_phase": "requirements" | "design" | "implementation" | "verification" | "maintenance",
    "source_uri": "gs://... or relative path",
    "parent_id": "uuid-of-parent-chunk",  # for Parent-Child
    "chunk_type": "child" | "parent" | "standalone"
}
```

These fields enable:

- Pre-filtering before (or after) vector search
- Deterministic assertions in evaluation (Lab 4)
- Better re-ranking signals (Lab 1.2)
- Traceability in the final compliance report (Capstone)

---

## 3. Bridging to Hybrid Retrieval

Once you have high-quality, metadata-rich chunks, the next step is retrieval that combines:

- **Dense vectors** (Vertex AI `text-embedding-004` or later) for semantic similarity
- **Sparse / keyword signals** (BM25 or equivalent) for exact control IDs, asset names, and rare technical terms
- **Reciprocal Rank Fusion (RRF)** or a learned re-ranker to merge the two ranked lists

Lab 1.2 will implement the hybrid + re-ranking layer. Lab 1.1 focuses on producing the clean, enriched corpus that makes hybrid retrieval effective.

---

## Recommended Python Building Blocks

```python
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from typing import List, Dict, Any
import uuid

# Example: header-aware splitting for an SDLC handbook
headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,
)

# Then enrich each resulting Document with domain metadata
# before writing to BigQuery or preparing for Vertex AI Vector Search.
```

---

## Key Takeaways

- Naive chunking destroys the hierarchical and cross-document relationships required for trustworthy DFD compliance evaluation.
- Document-aware splitting + Parent-Child indexing + rich domain metadata form the foundation of accurate RAG for security and architecture use cases.
- Everything built in Lab 1.1 becomes the corpus that Labs 1.2, 2.x, 3.x and the Capstone will query against.

**Next:** Implement the ingestion and enrichment pipeline in [Lab 1.1](lab-1.1.md).
