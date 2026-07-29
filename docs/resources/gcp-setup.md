# GCP Setup Scripts & Guidance

Place provisioning helpers in the repository under `/scripts`.

## Minimal Required APIs

- `aiplatform.googleapis.com`
- `alloydb.googleapis.com` (or `sqladmin.googleapis.com` for Cloud SQL)
- `bigquery.googleapis.com`
- `cloudbuild.googleapis.com`
- `secretmanager.googleapis.com`

## Recommended First Steps for Students

1. Create a dedicated GCP project (or use a sandbox).
2. Enable the APIs above.
3. Create a service account with least-privilege roles for the labs.
4. Run the provided bootstrap script (to be added) that creates a Vector Search index placeholder and an AlloyDB instance (or documents the manual steps).

Detailed scripts will be populated as labs are finalized.
