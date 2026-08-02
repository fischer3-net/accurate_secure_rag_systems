"""
Document-aware splitting and Parent-Child chunk construction for Lab 1.1.

Design goals
------------
* Preserve Markdown heading hierarchy (never split mid-control).
* Produce small, precise *child* chunks for retrieval precision.
* Produce richer *parent* chunks that supply surrounding context
  (Small-to-Big / Parent-Child pattern).
* Attach the full compliance metadata schema defined in metadata.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter

from .metadata import (
    ChunkRecord,
    ChunkType,
    DocType,
    enrich_chunk,
    validate_records,
)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
    ("####", "h4"),
]

# Map source filename → doc_type
DOC_TYPE_MAP = {
    "sdlc_handbook.md": DocType.SDLC_HANDBOOK.value,
    "security_baseline.md": DocType.SECURITY_BASELINE.value,
}


def _infer_doc_type(path: Path) -> str:
    name = path.name.lower()
    if name in DOC_TYPE_MAP:
        return DOC_TYPE_MAP[name]
    if "sdlc" in name or "handbook" in name:
        return DocType.SDLC_HANDBOOK.value
    if "security" in name or "baseline" in name or "control" in name:
        return DocType.SECURITY_BASELINE.value
    # Fallback – still valid, just less specific
    return DocType.SDLC_HANDBOOK.value


def _build_section_path(metadata: dict) -> str:
    """
    Reconstruct a human-readable hierarchical section path from the
    headers that MarkdownHeaderTextSplitter injects into Document.metadata.
    """
    parts: list[str] = []
    for key in ("h1", "h2", "h3", "h4"):
        if key in metadata and metadata[key]:
            parts.append(str(metadata[key]).strip())
    return " > ".join(parts) if parts else "root"


def _heading_path_list(metadata: dict) -> list[str]:
    return [
        str(metadata[k]).strip()
        for k in ("h1", "h2", "h3", "h4")
        if k in metadata and metadata[k]
    ]


# ---------------------------------------------------------------------------
# Core splitting
# ---------------------------------------------------------------------------

def split_markdown_file(
    path: Path | str,
    *,
    source_uri: Optional[str] = None,
    strip_headers: bool = False,
) -> list[Document]:
    """
    Split a Markdown policy document on heading boundaries.

    Returns a list of LangChain Documents whose .metadata already contains
    the heading hierarchy (h1/h2/h3/…).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Source document not found: {path}")

    text = path.read_text(encoding="utf-8")
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=strip_headers,
    )
    docs = splitter.split_text(text)

    # Attach provenance so later stages do not need the original Path
    uri = source_uri or str(path)
    for d in docs:
        d.metadata["source_uri"] = uri
        d.metadata["source_filename"] = path.name

    return docs


# ---------------------------------------------------------------------------
# Parent-Child construction
# ---------------------------------------------------------------------------

def build_parent_child_records(
    docs: list[Document],
    *,
    doc_type: str,
    source_uri: str,
    source_filename: Optional[str] = None,
    parent_strategy: str = "section",
) -> list[ChunkRecord]:
    """
    Convert header-split Documents into a Parent-Child corpus.

    Strategies
    ----------
    "section" (default)
        Group by the deepest common heading path. Each unique section
        becomes a *parent*; every leaf Document under that section becomes
        a *child* linked via parent_id.  If a section contains only one
        Document it is emitted as a standalone chunk (no artificial parent).

    "none"
        Emit every Document as a standalone chunk (useful for quick
        experiments or very flat documents).
    """
    if parent_strategy == "none":
        return [
            enrich_chunk(
                text=d.page_content,
                section=_build_section_path(d.metadata),
                doc_type=doc_type,
                source_uri=source_uri,
                chunk_type=ChunkType.STANDALONE.value,
                heading_path=_heading_path_list(d.metadata),
                source_filename=source_filename or d.metadata.get("source_filename"),
            )
            for d in docs
        ]

    # ---- "section" strategy ------------------------------------------------
    # Group documents by their full hierarchical path
    from collections import defaultdict

    groups: dict[str, list[Document]] = defaultdict(list)
    for d in docs:
        key = _build_section_path(d.metadata)
        groups[key].append(d)

    records: list[ChunkRecord] = []

    for section_path, group_docs in groups.items():
        if len(group_docs) == 1:
            # Single logical unit → standalone
            d = group_docs[0]
            records.append(
                enrich_chunk(
                    text=d.page_content,
                    section=section_path,
                    doc_type=doc_type,
                    source_uri=source_uri,
                    chunk_type=ChunkType.STANDALONE.value,
                    heading_path=_heading_path_list(d.metadata),
                    source_filename=source_filename
                    or d.metadata.get("source_filename"),
                )
            )
            continue

        # Multiple pieces under the same section → create a parent that
        # concatenates them, then emit each as a child.
        parent_text_parts = []
        for d in group_docs:
            parent_text_parts.append(d.page_content.strip())
        parent_text = "\n\n".join(parent_text_parts)

        parent = enrich_chunk(
            text=parent_text,
            section=section_path,
            doc_type=doc_type,
            source_uri=source_uri,
            chunk_type=ChunkType.PARENT.value,
            heading_path=_heading_path_list(group_docs[0].metadata),
            source_filename=source_filename
            or group_docs[0].metadata.get("source_filename"),
        )
        records.append(parent)

        for d in group_docs:
            child = enrich_chunk(
                text=d.page_content,
                section=section_path,
                doc_type=doc_type,
                source_uri=source_uri,
                chunk_type=ChunkType.CHILD.value,
                parent_id=parent.chunk_id,
                heading_path=_heading_path_list(d.metadata),
                source_filename=source_filename
                or d.metadata.get("source_filename"),
            )
            records.append(child)

    return records


# ---------------------------------------------------------------------------
# High-level convenience API
# ---------------------------------------------------------------------------

def process_document(
    path: Path | str,
    *,
    source_uri: Optional[str] = None,
    parent_strategy: str = "section",
    strip_headers: bool = False,
) -> list[ChunkRecord]:
    """
    End-to-end: load Markdown → header-aware split → Parent-Child records
    with full metadata enrichment.
    """
    path = Path(path)
    uri = source_uri or str(path)
    doc_type = _infer_doc_type(path)

    docs = split_markdown_file(path, source_uri=uri, strip_headers=strip_headers)
    records = build_parent_child_records(
        docs,
        doc_type=doc_type,
        source_uri=uri,
        source_filename=path.name,
        parent_strategy=parent_strategy,
    )
    return records


def process_directory(
    data_dir: Path | str,
    *,
    parent_strategy: str = "section",
    pattern: str = "*.md",
) -> list[ChunkRecord]:
    """
    Process every Markdown file in a directory and return a combined corpus.
    """
    data_dir = Path(data_dir)
    all_records: list[ChunkRecord] = []

    for path in sorted(data_dir.glob(pattern)):
        if path.is_file():
            recs = process_document(path, parent_strategy=parent_strategy)
            all_records.extend(recs)

    # Final validation
    errors = validate_records(all_records)
    if errors:
        # Surface problems early; do not silently produce a broken corpus
        msg = "Corpus validation failed:\n  - " + "\n  - ".join(errors)
        raise ValueError(msg)

    return all_records
