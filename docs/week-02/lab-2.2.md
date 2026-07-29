# Lab 2.2 – Graph-Augmented RAG for DFD Connectivity

**Objective:** Model DFD elements (Process, Data Store, External Entity, Data Flow, Trust Boundary) as a graph and combine graph traversal with vector retrieval for structural validation against SDLC trust-boundary rules.

## Deliverables

- Graph schema and ingestion script (Neo4j or Spanner Graph).
- Hybrid query that first expands the relevant subgraph, then performs semantic search over the linked policy chunks.
- Demonstration that pure vector search misses certain structural violations that the graph path catches.

## Starter Location

```
labs/02-storage/
notebooks/lab-2.2-graph-rag.ipynb
```
