"""
Persistence helpers for the Lab 1.1 enriched corpus.

Supported targets
-----------------
1. BigQuery table (primary – excellent for inspection, SQL filtering,
   and later hybrid SQL + vector queries).
2. Local JSONL (ready for Vertex AI Vector Search index creation or
   offline evaluation).

Both writers are idempotent when you supply a consistent chunk_id.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Sequence

from .metadata import ChunkRecord


# ---------------------------------------------------------------------------
# BigQuery schema (mirrors ChunkRecord)
# ---------------------------------------------------------------------------

BIGQUERY_SCHEMA = [
    {"name": "chunk_id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "doc_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "section", "type": "STRING", "mode": "REQUIRED"},
    {"name": "control_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "asset_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "risk_tier", "type": "STRING", "mode": "REQUIRED"},
    {"name": "sdlc_phase", "type": "STRING", "mode": "REQUIRED"},
    {"name": "source_uri", "type": "STRING", "mode": "REQUIRED"},
    {"name": "parent_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "chunk_type", "type": "STRING", "mode": "REQUIRED"},
    {"name": "text", "type": "STRING", "mode": "REQUIRED"},
    {"name": "token_count", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "heading_path", "type": "STRING", "mode": "REPEATED"},
    {"name": "source_filename", "type": "STRING", "mode": "NULLABLE"},
]


def _records_to_rows(records: Sequence[ChunkRecord]) -> list[dict[str, Any]]:
    rows = []
    for r in records:
        d = r.to_dict()
        # BigQuery REPEATED fields prefer a plain list; None → []
        if d.get("heading_path") is None:
            d["heading_path"] = []
        rows.append(d)
    return rows


def write_jsonl(
    records: Sequence[ChunkRecord],
    path: Path | str,
    *,
    overwrite: bool = True,
) -> Path:
    """
    Write the corpus to a JSONL file (one ChunkRecord per line).

    This format is convenient for:
    - offline inspection
    - Vertex AI Vector Search batch index creation
    - evaluation harnesses that do not yet talk to BigQuery
    """
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing file: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    return path


def load_jsonl(path: Path | str) -> list[ChunkRecord]:
    """Inverse of write_jsonl – useful for tests and later labs."""
    path = Path(path)
    records: list[ChunkRecord] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(ChunkRecord.model_validate(json.loads(line)))
    return records


# ---------------------------------------------------------------------------
# BigQuery
# ---------------------------------------------------------------------------

def ensure_bigquery_table(
    project_id: str,
    dataset_id: str,
    table_id: str = "rag_chunks",
    *,
    location: str = "US",
) -> str:
    """
    Create the dataset + table if they do not already exist.
    Returns the fully-qualified table id.
    """
    from google.cloud import bigquery

    client = bigquery.Client(project=project_id, location=location)

    # Dataset
    dataset_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset_ref.location = location
    client.create_dataset(dataset_ref, exists_ok=True)

    # Table
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    schema = [bigquery.SchemaField(**f) for f in BIGQUERY_SCHEMA]
    table = bigquery.Table(table_ref, schema=schema)
    client.create_table(table, exists_ok=True)

    return table_ref


def write_bigquery(
    records: Sequence[ChunkRecord],
    *,
    project_id: Optional[str] = None,
    dataset_id: str = "rag_lab",
    table_id: str = "rag_chunks",
    location: str = "US",
    write_disposition: str = "WRITE_TRUNCATE",
) -> str:
    """
    Load the enriched corpus into BigQuery.

    Parameters
    ----------
    write_disposition :
        "WRITE_TRUNCATE" – replace the whole table (safe for lab re-runs).
        "WRITE_APPEND"   – append (you must guarantee no duplicate chunk_ids).
    """
    from google.cloud import bigquery

    project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError(
            "project_id must be supplied or GOOGLE_CLOUD_PROJECT must be set"
        )

    table_ref = ensure_bigquery_table(
        project_id, dataset_id, table_id, location=location
    )

    client = bigquery.Client(project=project_id, location=location)
    rows = _records_to_rows(records)

    job_config = bigquery.LoadJobConfig(
        schema=[bigquery.SchemaField(**f) for f in BIGQUERY_SCHEMA],
        write_disposition=write_disposition,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    # Load from in-memory list of dicts
    job = client.load_table_from_json(rows, table_ref, job_config=job_config)
    job.result()  # wait for completion

    return table_ref


def query_chunks(
    sql: str,
    *,
    project_id: Optional[str] = None,
    location: str = "US",
) -> list[dict[str, Any]]:
    """
    Convenience helper for ad-hoc inspection queries.
    Example:
        SELECT control_id, section, risk_tier
        FROM `project.rag_lab.rag_chunks`
        WHERE asset_type = 'trust_boundary'
    """
    from google.cloud import bigquery

    project_id = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT")
    client = bigquery.Client(project=project_id, location=location)
    result = client.query(sql).result()
    return [dict(row) for row in result]
