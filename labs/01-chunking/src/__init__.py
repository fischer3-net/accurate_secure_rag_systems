"""
Lab 1.x – Chunking, metadata enrichment, and hybrid retrieval package.

Public API
----------
from src.chunking import process_document, process_directory
from src.metadata import ChunkRecord, validate_records
from src.ingest import write_jsonl, write_bigquery, load_jsonl
from src.retrieval import HybridRetriever, evaluate_retriever
"""

from .chunking import process_document, process_directory, split_markdown_file
from .metadata import ChunkRecord, validate_records, enrich_chunk
from .ingest import write_jsonl, write_bigquery, load_jsonl, ensure_bigquery_table
from .retrieval import (
    HybridRetriever,
    BM25Index,
    DenseIndex,
    HashingEmbedder,
    VertexEmbedder,
    reciprocal_rank_fusion,
    simple_rerank,
    evaluate_retriever,
    load_eval_queries,
    precision_at_k,
)

__all__ = [
    # Lab 1.1
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
    # Lab 1.2
    "HybridRetriever",
    "BM25Index",
    "DenseIndex",
    "HashingEmbedder",
    "VertexEmbedder",
    "reciprocal_rank_fusion",
    "simple_rerank",
    "evaluate_retriever",
    "load_eval_queries",
    "precision_at_k",
]
