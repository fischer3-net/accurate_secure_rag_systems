# Optional: Provision AlloyDB / Cloud SQL + pgvector

This lab runs offline with `PgVectorStore`. Use the steps below when you want a real managed PostgreSQL + pgvector backend.

## Cloud SQL for PostgreSQL (simplest workshop path)

```bash
gcloud sql instances create rag-pg \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --root-password=CHANGE_ME

gcloud sql databases create rag --instance=rag-pg
```

Connect and enable the extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE rag_chunks (
  chunk_id TEXT PRIMARY KEY,
  doc_type TEXT,
  section TEXT,
  control_id TEXT,
  asset_type TEXT,
  risk_tier TEXT,
  sdlc_phase TEXT,
  source_uri TEXT,
  parent_id TEXT,
  chunk_type TEXT,
  text TEXT,
  embedding vector(768)   -- match your embedding model dimension
);

CREATE INDEX ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

Point a thin adapter at this table (psycopg / asyncpg) that implements the same `upsert` / `search` interface as `PgVectorStore`.

## AlloyDB

Similar SQL; prefer AlloyDB when you need higher performance column store / HTAP features. Enable `google_ml_integration` if you want in-database embedding calls.
