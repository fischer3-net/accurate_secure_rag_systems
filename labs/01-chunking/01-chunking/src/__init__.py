"""
Lab 1.1 – Document-aware chunking & metadata enrichment package.

Public API
----------
from src.chunking import process_document, process_directory
from src.metadata import ChunkRecord, validate_records
from src.ingest import write_jsonl, write_bigquery, load_jsonl
"""

from .chunking import process_document, process_directory, split_markdown_file
from .metadata import ChunkRecord, validate_records, enrich_chunk
from .ingest import write_jsonl, write_bigquery, load_jsonl, ensure_bigquery_table

__all__ = [
    "process_document",
    "process_directory",
    "split_markdown_file",
    "ChunkRecord",
    "validate_records",
    "enrich_chunk",
    "write_jsonl",
    "write_bigquery",
    "load_jsonl",
    "ensure_bigquery_table",
]
