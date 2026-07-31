# Optional: Provision Vertex AI Vector Search

This lab runs offline with `VectorSearchStore`. Use the steps below for a real Matching Engine index.

1. Create a GCS bucket and upload JSONL documents (id + embedding + restricts).
2. Create an index:

```bash
gcloud ai indexes create \
  --display-name=rag-security-controls \
  --metadata-file=index_metadata.json \
  --region=us-central1
```

3. Deploy an index endpoint and query via the Vertex AI SDK.

Map restricts to the metadata fields you already enrich in Lab 1.1 (`asset_type`, `risk_tier`, `sdlc_phase`, …). Keep the same `search(...)` signature used by `VectorSearchStore` so Capstone skills stay backend-agnostic.
