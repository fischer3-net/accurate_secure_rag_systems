# Lab 2.1 – AlloyDB pgvector vs Vertex AI Vector Search

**Objective:** Provision both stores, load the same enriched security-rule corpus, and benchmark retrieval quality + latency for structured security rule lookups.

## Deliverables

- Provisioning scripts (Terraform or `gcloud` / Python) for both options.
- Side-by-side benchmark notebook measuring:
  - Recall / precision on a fixed query set
  - p50 / p95 latency
  - Cost estimate for the lab workload
- Recommendation memo (short Markdown) justifying the choice for the DFD compliance scenario.

## Starter Location

```
labs/02-storage/
scripts/provision-alloydb.sh
scripts/provision-vector-search.sh
notebooks/lab-2.1-benchmark.ipynb
```
