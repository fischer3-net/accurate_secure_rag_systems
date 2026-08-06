# Week 1 Theory – Precision RAG & Domain Chunking for Compliance Data

**Focus:** Why naive RAG fails on multi-document compliance tasks and how to design chunking + metadata strategies that preserve hierarchical and cross-document relationships.

Welcome to Week 1. If you’ve ever tried to build a RAG system that can answer a real security architecture question—something like “Does this Data Flow Diagram violate any controls in our SDLC handbook or the technical security baseline?”—you’ve probably already felt the pain. The system either retrieves the wrong fragments, loses critical context, or worse, invents plausible-sounding compliance statements that no human reviewer would accept.

This week is about fixing that foundation. We move beyond “just chunk and embed” and treat retrieval as a deliberate design problem for compliance-grade accuracy.

---

## 1. The Multi-Document Alignment Problem

Security and architecture teams don’t ask isolated questions about a single document. They ask questions that require simultaneous reasoning across multiple sources of truth:

> “Does this Data Flow Diagram violate any controls in our SDLC handbook or the technical security baseline regarding trust boundaries and external entity access?”

That single question forces the system to align three very different kinds of content:

| Document Type              | Typical Structure                                      | Granularity of Interest          |
|----------------------------|--------------------------------------------------------|----------------------------------|
| Data Flow Diagram (DFD)    | Processes, Data Stores, External Entities, Data Flows, Trust Boundaries | Component / edge level           |
| SDLC Handbook              | Hierarchical sections, gates, phase requirements       | Section / control level          |
| Technical Security Baseline| Numbered controls, risk statements, implementation guidance | Individual control or sub-control|

These documents speak different languages and operate at different levels of abstraction. A DFD is a graph of elements and relationships. An SDLC handbook is a hierarchical policy narrative. A security baseline is a flat (or lightly nested) catalogue of discrete controls. Getting a retrieval system to treat them as a coherent knowledge base is the core challenge of this week.

### Why standard “naive RAG” fails here

Most off-the-shelf RAG pipelines apply a fixed-size or simple recursive splitter and hope for the best. That approach collapses under the weight of real compliance work for four reasons:

1. **Hierarchy mismatch**  
   A fixed-size or pure semantic chunk from the SDLC handbook frequently contains only a partial control statement. The corresponding DFD element may need the parent section context (e.g., “Phase 3 – Architecture Review Gate”) to be correctly evaluated. Without that parent context, the LLM is forced to guess the broader rule, and guessing is exactly what we cannot tolerate in a security setting.

2. **Cross-document entity resolution**  
   Terms such as “External Entity”, “Trust Boundary”, “Data Store”, or specific asset names appear in both the diagram and the policy documents—but with different surrounding language and different levels of formality. Pure vector similarity often retrieves the wrong sense of the term. You end up with a chunk that talks about external entities in a completely different regulatory context.

3. **Loss of structural relationships**  
   Security evaluation frequently depends on connectivity: Process → Data Store → External Entity, and especially on whether a flow crosses a trust boundary. Flat chunks destroy this graph-like information. Once the edges are gone, the model can no longer reason about paths or boundary crossings.

4. **Hallucination under sparse retrieval**  
   When the top-k retrieved chunks do not contain the exact control language the question needs, the LLM tends to invent plausible but non-grounded compliance statements. In a security review that behaviour is unacceptable. We need retrieval that is precise enough that the model rarely has to fill gaps with imagination.

**Goal of this week:** Build a retrieval foundation that preserves hierarchy, enriches domain metadata, and surfaces the right policy context for any given DFD element or flow. Everything that follows in Labs 1.1 and 1.2, and ultimately the Capstone, rests on this foundation.

---

## 2. Advanced Chunking Strategies in Python

### 2.1 Beyond Fixed-Size Chunking

Fixed-size (or even recursive character) splitters are convenient. They are also the single most common reason compliance RAG systems under-perform. Logical units that matter for security get arbitrarily cut:

- A security control should rarely be split mid-sentence.
- A Markdown heading hierarchy in an SDLC handbook is a strong, reliable signal of semantic boundaries.
- JSON or XML representations of DFDs have explicit element boundaries that should be respected rather than ignored.

**Preferred approaches for this course:**

| Strategy                  | When to use                                      | Library / Technique                              |
|---------------------------|--------------------------------------------------|--------------------------------------------------|
| Markdown header-aware     | SDLC handbooks, security baselines written in Markdown | `MarkdownHeaderTextSplitter`                     |
| Document-structure aware  | Structured policy (JSON, XML, YAML)              | Custom recursive split on keys / tags            |
| Parent-Child (Small-to-Big)| Dense control catalogues                         | Store small precise chunks + larger parent context |
| Semantic chunking         | Long narrative sections                          | Embedding-based boundary detection (use sparingly)|

Markdown header-aware splitting is our default starting point for the policy documents you will work with this week. It respects the document author’s own structure instead of imposing an arbitrary token window.

### 2.2 Parent-Child / Small-to-Big Retrieval

This pattern is particularly powerful for security standards and is one of the core techniques you will implement in Lab 1.1.

- **Child chunks** are small, precise units—individual controls or sub-requirements. They are ideal for accurate vector matching.
- **Parent chunks** contain the surrounding section, the rationale, related controls, and any phase or gate context.
- At retrieval time you surface the child (for precision) **and** the parent (for context), or you expand to the parent after the child is selected.

This design avoids the classic trade-off between “too small → loses meaning” and “too large → dilutes relevance.” The child gives you a high-precision hit; the parent restores the hierarchical context the security reviewer actually needs.

In practice you will store both, link them with a `parent_id`, and decide at query time whether to return the child alone, the parent alone, or both. That flexibility becomes extremely useful later when you start evaluating retrieval quality (Week 4).

### 2.3 Metadata Enrichment (Critical for Compliance)

Raw text chunks are rarely enough. Once you move into production security use cases you will want to filter, rank, and audit retrieval results using domain knowledge that lives outside the text itself. For DFD security evaluation we recommend a consistent metadata schema from day one:

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

These fields enable several capabilities that pure vector search cannot provide:

- **Pre-filtering** before (or after) vector search – e.g., only retrieve controls that apply to the Design phase or that mention trust boundaries.
- **Deterministic assertions** in evaluation (Lab 4) – you can write tests that check whether a required control_id or risk_tier appeared in the retrieved set.
- **Better re-ranking signals** (Lab 1.2) – metadata becomes an additional ranking feature alongside semantic similarity and keyword match.
- **Traceability** in the final compliance report (Capstone) – every claim can be traced back to a specific source_uri, section, and control_id.

Treat metadata as first-class data, not an afterthought. The schema above is the minimum you should aim for; you are free to extend it, but do not remove the core fields—later labs and the Capstone evaluation suite expect them.

---

## 3. Bridging to Hybrid Retrieval

High-quality, metadata-rich chunks are necessary but not sufficient. Once you have them, the next design decision is how you actually retrieve.

Pure dense retrieval (embeddings only) is excellent at semantic similarity but weak on exact control IDs, rare technical terms, and precise asset names. Pure keyword search (BM25 or equivalent) is the opposite: excellent on exact matches, weaker on paraphrases. The practical answer for compliance workloads is hybrid retrieval:

- **Dense vectors** (Vertex AI `text-embedding-004` or later) for semantic similarity
- **Sparse / keyword signals** (BM25 or equivalent) for exact control IDs, asset names, and rare technical terms
- **Reciprocal Rank Fusion (RRF)** or a learned re-ranker to merge the two ranked lists into a single high-quality ranking

Lab 1.2 implements the hybrid + re-ranking layer. Lab 1.1 focuses on producing the clean, enriched corpus that makes hybrid retrieval effective. If the chunks going into the index are poorly structured or missing metadata, no amount of fancy fusion will save you.

---

## Recommended Python Building Blocks

Here is a minimal, realistic starting point using LangChain’s text splitters. You will expand this significantly in the lab, but the pattern is already visible:

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
    strip_headers=False,          # keep the headers in the chunk text
)

# After splitting, enrich each resulting Document with domain metadata
# before writing to BigQuery or preparing for Vertex AI Vector Search.
# Parent-Child linking and risk-tier / asset-type tagging happen in this
# enrichment step.
```

In Lab 1.1 you will turn this sketch into a full, testable pipeline that also handles Parent-Child relationships and the complete metadata schema shown earlier.

---

## Key Takeaways

- Naive chunking destroys the hierarchical and cross-document relationships required for trustworthy DFD compliance evaluation.
- Document-aware splitting + Parent-Child indexing + rich domain metadata form the foundation of accurate RAG for security and architecture use cases.
- Everything built in Lab 1.1 becomes the corpus that Labs 1.2, 2.x, 3.x and the Capstone will query against. Invest the time to get the chunks and metadata right; the rest of the course builds on this work.

**Next:** Implement the ingestion and enrichment pipeline in [Lab 1.1](lab-1.1.md).

---



## Addendum: Mathematical Foundations  (Completely OPTIONAL)

The formulas below underpin the retrieval ideas introduced this week. They will reappear in Lab 1.2 (hybrid retrieval + RRF) and again in the evaluation work of Week 4.

### A.1 Dense Retrieval – Cosine Similarity

Modern embedding models map text to high-dimensional vectors. The most common similarity measure between a query vector \(\mathbf{q}\) and a document vector \(\mathbf{d}\) is cosine similarity:

\[
\text{sim}_{\cos}(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|}
\]

When both vectors are L2-normalised (a common practice), this simplifies to the inner product:

\[
\text{sim}_{\cos}(\mathbf{q}, \mathbf{d}) = \mathbf{q} \cdot \mathbf{d}
\]

Dense retrieval ranks documents by this score. It excels at semantic paraphrases (“unprotected flows across trust boundaries”) but is weaker on exact control IDs and rare technical terms.

### A.2 Sparse Retrieval – BM25

BM25 is the classic bag-of-words ranking function. For a query \(q\) containing terms \(t\), the score of a document \(d\) is:

\[
\text{BM25}(q, d) = \sum_{t \in q} \text{IDF}(t) \cdot \frac{f(t, d) \cdot (k_1 + 1)}{f(t, d) + k_1 \cdot \bigl(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\bigr)}
\]

where:

- \(f(t, d)\) is the term frequency of \(t\) in \(d\)
- \(|d|\) is the length of document \(d\)
- \(\text{avgdl}\) is the average document length in the collection
- \(k_1\) and \(b\) are free parameters (typical defaults: \(k_1 = 1.2\), \(b = 0.75\))
- \(\text{IDF}(t)\) is an inverse-document-frequency weight that down-weights common terms

BM25 is excellent at exact control IDs (`SEC-DFD-014`), asset names, and regulatory language—the complementary strength to dense embeddings.

### A.3 Reciprocal Rank Fusion (RRF)

When you have two (or more) ranked lists—one from dense retrieval, one from BM25—you need a way to merge them without assuming the scores are on the same numeric scale. Reciprocal Rank Fusion does exactly that:

\[
\text{score}_{\text{RRF}}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}_r(d)}
\]

- \(R\) is the set of ranked lists (dense, sparse, \ldots)
- \(\text{rank}_r(d)\) is the 1-based rank of document \(d\) in list \(r\) (or a large constant if \(d\) does not appear)
- \(k = 60\) is the conventional constant that softens the impact of very high ranks

RRF needs no score normalisation and remains stable when the underlying retrievers produce incomparable score ranges. This is why it is the default fusion method in Lab 1.2.

### A.4 Why Parent-Child Helps Information Density

A short mathematical intuition for the Parent-Child (Small-to-Big) pattern:

Let \(c\) be a small child chunk (high precision, lower context) and \(p\) its parent (higher context, potentially diluted relevance).  
At retrieval time we can:

1. Rank by the child embedding: \(\text{sim}(q, c)\) — maximises precision.
2. Expand to the parent text for the final context window: the LLM receives \(p\) (or \(c \oplus p\)).

This separates the *matching* problem (best solved by a tight semantic unit) from the *context* problem (best solved by the surrounding hierarchical section). The net effect is higher effective information density in the prompt without sacrificing retrieval precision.
