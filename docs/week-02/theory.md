# Week 2 Theory – Storage Architecture on GCP

!!! note "Status"
    Skeleton page. Expand with detailed comparison tables, latency/cost numbers, and decision trees.

## Deconstructing RAG Storage Options on GCP

- **Vertex AI Vector Search (Matching Engine):** Ultra-low latency, billion-scale ANN. When to use and when it is overkill.
- **AlloyDB / Cloud SQL with `pgvector`:** Hybrid relational + vector. Ideal for SQL filtering + semantic retrieval.
- **BigQuery Vector Search:** Large-scale batch / analytics-driven RAG.
- **Knowledge Graphs (Neo4j / Spanner Graph):** Lineage, data-flow connectivity, structural relationship validation (Process → Data Store → External Entity).

## Architectural Trade-off Matrix

| Dimension | Vertex AI Vector Search | AlloyDB + pgvector | BigQuery | Graph (Neo4j/Spanner) |
|-----------|-------------------------|--------------------|----------|-----------------------|
| Latency   | Extremely low           | Low–Medium         | Higher   | Medium                |
| Cost model| Index + query units     | Instance + storage | Scan-based | Instance + storage  |
| Hybrid SQL| Limited                 | Native             | Strong   | Limited               |
| Graph queries | No                   | Limited            | No       | Native                |
| Ops complexity | Low                  | Medium             | Low      | Higher                |

## Decision Guidance

Choose storage according to the dominant query pattern in the DFD compliance use case.
