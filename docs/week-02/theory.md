# Week 2 Theory – Storage Architecture on Google Cloud Platform

**Focus:** Choosing the right place to store and query the enriched compliance corpus so that DFD security evaluation is fast, accurate, and operationally sustainable.

---

## 1. Why Storage Choice Matters for Compliance RAG

In Week 1 you built a high-quality, metadata-rich corpus of SDLC and security-baseline chunks. That corpus is now small enough to live in memory, but a production DFD compliance system will grow to:

- Hundreds of policy documents and control libraries
- Thousands of historical DFD evaluations
- Continuous updates as baselines change

The storage layer determines:

| Concern | Impact on DFD compliance |
|---------|---------------------------|
| **Latency** | Interactive review tools need sub-second answers |
| **Hybrid filtering** | “Show only *critical* trust-boundary controls in the *Design* phase” is a SQL + vector query |
| **Structural queries** | “Does any data flow from External Entity X reach Data Store Y without crossing an authenticated process?” is a graph query |
| **Cost & ops** | Workshop vs. production budgets; who patches the database? |
| **Auditability** | Can you prove which version of a control was retrieved on a given date? |

No single GCP product wins on every axis. The skill is matching the **dominant query pattern** to the right engine (or combination).

---

## 2. Deconstructing the GCP Options

### 2.1 Vertex AI Vector Search (Matching Engine)

- **What it is:** Managed approximate nearest-neighbour (ANN) service built for billion-scale vector retrieval.
- **Strengths:** Extremely low latency at scale, automatic sharding, tight integration with Vertex AI embeddings and Ranking API.
- **Weaknesses:** Limited native metadata filtering compared with a relational store; cost is driven by index size + query volume; overkill for corpora under ~100 k vectors if you already have a database.
- **Best when:** You need pure semantic search at high QPS and can accept (or implement) filtering in application code or via restricted metadata.

### 2.2 AlloyDB / Cloud SQL with `pgvector`

- **What it is:** PostgreSQL-compatible managed database with the `pgvector` extension for exact or approximate vector search *inside* SQL.
- **Strengths:** True hybrid queries (`WHERE risk_tier = 'critical' ORDER BY embedding <=> $1`), transactional consistency, familiar SQL tooling, Point-in-Time recovery.
- **Weaknesses:** You manage (or pay for) instance sizing; ANN performance is good but not in the same league as Matching Engine at extreme scale.
- **Best when:** The majority of queries combine structured filters (control_id, asset_type, sdlc_phase, risk_tier) with semantic similarity — exactly the pattern of DFD policy lookup.

### 2.3 BigQuery Vector Search

- **What it is:** Vector similarity as a SQL function inside BigQuery.
- **Strengths:** Serverless, excellent for batch analysis, joins against large analytic tables, cost is scan-based.
- **Weaknesses:** Higher latency than online serving stores; not ideal for interactive sub-100 ms responses.
- **Best when:** Offline evaluation, audit reporting, or joining retrieved chunks with large historical DFD evaluation logs.

### 2.4 Knowledge Graphs (Neo4j on GKE / Aura, or Spanner Graph)

- **What it is:** First-class graph storage and traversal (Cypher or GQL).
- **Strengths:** Natural model for DFD topology (Process → DataFlow → DataStore, TrustBoundary edges, ExternalEntity nodes). Path queries answer structural compliance questions that pure vector search cannot.
- **Weaknesses:** Operational overhead; vector search is secondary (or requires a dual-write pattern).
- **Best when:** You must validate *connectivity* and *trust-boundary crossings*, not only “which policy text is similar to this question.”

---

## 3. Architectural Trade-off Matrix

| Dimension | Vertex AI Vector Search | AlloyDB + pgvector | BigQuery Vector | Graph (Neo4j / Spanner Graph) |
|-----------|-------------------------|--------------------|-----------------|-------------------------------|
| **p50 latency (online)** | Extremely low | Low–medium | Higher | Medium |
| **Hybrid SQL + vector** | Limited | **Native** | Strong | Limited |
| **Graph / path queries** | No | Limited | No | **Native** |
| **Scale (vectors)** | Billions | Millions (practical) | Billions (batch) | Millions of nodes/edges |
| **Cost model** | Index + query units | Instance + storage | Scan / slot | Instance + storage |
| **Ops complexity** | Low (managed) | Medium | Low | Higher |
| **Transactional updates** | Eventual | Strong | Append-oriented | Strong |
| **Audit / versioning** | Application-level | Easy (tables + history) | Excellent | Application-level |

---

## 4. Decision Guidance for the DFD Compliance Use Case

```
Is the dominant need structural / path validation
(e.g. “does this flow cross a trust boundary without controls”)?
        │
        ├─ YES → Graph store (Neo4j or Spanner Graph)
        │         + vector index for the linked policy text
        │
        └─ NO
             │
             Is the dominant need interactive hybrid
             (metadata filter + semantic similarity)?
                    │
                    ├─ YES → AlloyDB / Cloud SQL + pgvector
                    │         (or Vertex AI Vector Search + app-side filter
                    │          if QPS / scale demands it)
                    │
                    └─ Batch / analytics / audit only?
                              │
                              └─ BigQuery Vector Search
```

**Practical hybrid pattern used in many production systems (and in the Capstone):**

1. **AlloyDB (or Cloud SQL) + pgvector** as the system of record for chunks + metadata.
2. Optional **Vertex AI Vector Search** replica for ultra-low-latency pure semantic endpoints.
3. Optional **graph overlay** (Neo4j / Spanner Graph) for DFD topology, with edges that point back to chunk IDs in the relational/vector store.

---

## 5. Mapping Week 1 Artefacts to Storage

| Week 1 artefact | Natural home |
|-----------------|--------------|
| Enriched chunks (`ChunkRecord`) | AlloyDB table or Vertex AI index documents |
| Metadata filters (asset_type, risk_tier, …) | SQL `WHERE` or Vertex restrict tokens |
| Parent–Child links | Self-referential foreign key or graph edge |
| Evaluation queries | BigQuery table for offline scoring |
| DFD topology (Lab 2.2) | Graph nodes + edges |

---

## 6. Key Takeaways

- Storage is a **query-pattern** decision, not a popularity contest.
- For DFD security evaluation the two most valuable capabilities are **hybrid SQL + vector** (AlloyDB/pgvector) and **path / connectivity queries** (graph).
- Vertex AI Vector Search shines when pure semantic latency at scale is the bottleneck.
- BigQuery is the natural home for evaluation, audit, and batch re-scoring.
- The Capstone will ask you to justify and implement at least one hybrid pattern.

**Next:** Lab 2.1 benchmarks AlloyDB-style hybrid retrieval against a Vector Search-style pure semantic path. Lab 2.2 adds the graph layer for structural validation.
