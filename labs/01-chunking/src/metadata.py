"""
Domain metadata schema and deterministic enrichment for Lab 1.1.

This module defines the canonical compliance-oriented metadata that every
chunk in the course corpus must carry. Enrichment is rule-based so that
control identifiers, risk tiers, and asset types remain auditable and
reproducible — critical for security and architecture use cases.
"""

from __future__ import annotations

import re
import uuid
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums (kept as strings in the model for BigQuery / JSON compatibility)
# ---------------------------------------------------------------------------

class DocType(str, Enum):
    SDLC_HANDBOOK = "sdlc_handbook"
    SECURITY_BASELINE = "security_baseline"
    DFD = "dfd"  # reserved for later labs / Capstone


class AssetType(str, Enum):
    PROCESS = "process"
    DATA_STORE = "data_store"
    EXTERNAL_ENTITY = "external_entity"
    TRUST_BOUNDARY = "trust_boundary"
    DATA_FLOW = "data_flow"
    GENERAL = "general"


class RiskTier(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNSPECIFIED = "unspecified"


class SdlcPhase(str, Enum):
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    VERIFICATION = "verification"
    MAINTENANCE = "maintenance"
    GENERAL = "general"


class ChunkType(str, Enum):
    CHILD = "child"
    PARENT = "parent"
    STANDALONE = "standalone"


# ---------------------------------------------------------------------------
# Canonical chunk record
# ---------------------------------------------------------------------------

class ChunkRecord(BaseModel):
    """
    Canonical metadata + content record for every chunk produced by Lab 1.1.

    This schema is intentionally strict: later labs (hybrid retrieval,
    evaluation, Capstone) depend on these fields being present and typed.
    """

    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    doc_type: str
    section: str
    control_id: Optional[str] = None
    asset_type: str = AssetType.GENERAL.value
    risk_tier: str = RiskTier.UNSPECIFIED.value
    sdlc_phase: str = SdlcPhase.GENERAL.value
    source_uri: str
    parent_id: Optional[str] = None
    chunk_type: str = ChunkType.STANDALONE.value
    text: str
    token_count: Optional[int] = None

    # Optional audit / debugging fields (not required by the lab schema
    # but useful for reproducibility)
    heading_path: Optional[list[str]] = None
    source_filename: Optional[str] = None

    @field_validator("doc_type")
    @classmethod
    def validate_doc_type(cls, v: str) -> str:
        allowed = {e.value for e in DocType}
        if v not in allowed:
            raise ValueError(f"doc_type must be one of {allowed}, got {v!r}")
        return v

    @field_validator("asset_type")
    @classmethod
    def validate_asset_type(cls, v: str) -> str:
        allowed = {e.value for e in AssetType}
        if v not in allowed:
            raise ValueError(f"asset_type must be one of {allowed}, got {v!r}")
        return v

    @field_validator("risk_tier")
    @classmethod
    def validate_risk_tier(cls, v: str) -> str:
        allowed = {e.value for e in RiskTier}
        if v not in allowed:
            raise ValueError(f"risk_tier must be one of {allowed}, got {v!r}")
        return v

    @field_validator("sdlc_phase")
    @classmethod
    def validate_sdlc_phase(cls, v: str) -> str:
        allowed = {e.value for e in SdlcPhase}
        if v not in allowed:
            raise ValueError(f"sdlc_phase must be one of {allowed}, got {v!r}")
        return v

    @field_validator("chunk_type")
    @classmethod
    def validate_chunk_type(cls, v: str) -> str:
        allowed = {e.value for e in ChunkType}
        if v not in allowed:
            raise ValueError(f"chunk_type must be one of {allowed}, got {v!r}")
        return v

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict suitable for BigQuery / JSONL."""
        return self.model_dump(mode="python")


# ---------------------------------------------------------------------------
# Deterministic enrichment rules
# ---------------------------------------------------------------------------

# Control ID pattern used in the sample security baseline and many real
# baselines (e.g. SEC-DFD-014, AC-3, SI-4(5), etc.)
CONTROL_ID_RE = re.compile(
    r"\b("
    r"SEC-[A-Z]+-\d+"          # SEC-DFD-014 style
    r"|[A-Z]{1,4}-\d+(?:\([0-9a-z]+\))?"  # NIST-style AC-3, SI-4(5)
    r")\b",
    re.IGNORECASE,
)

# Keyword → asset_type mapping (order matters: more specific first)
ASSET_KEYWORDS: list[tuple[str, str]] = [
    (r"\btrust\s+boundar(?:y|ies)\b", AssetType.TRUST_BOUNDARY.value),
    (r"\bexternal\s+entit(?:y|ies)\b", AssetType.EXTERNAL_ENTITY.value),
    (r"\bdata\s+store(?:s)?\b", AssetType.DATA_STORE.value),
    (r"\bdata\s+flow(?:s)?\b", AssetType.DATA_FLOW.value),
    (r"\bprocess(?:es)?\b", AssetType.PROCESS.value),
]

# Keyword → risk_tier (explicit statements take precedence)
RISK_KEYWORDS: list[tuple[str, str]] = [
    (r"\bcritical\b", RiskTier.CRITICAL.value),
    (r"\bhigh\b", RiskTier.HIGH.value),
    (r"\bmedium\b", RiskTier.MEDIUM.value),
    (r"\blow\b", RiskTier.LOW.value),
]

# Keyword / section → sdlc_phase
PHASE_KEYWORDS: list[tuple[str, str]] = [
    (r"\brequirements?\b", SdlcPhase.REQUIREMENTS.value),
    (r"\bdesign\b", SdlcPhase.DESIGN.value),
    (r"\bimplementation\b", SdlcPhase.IMPLEMENTATION.value),
    (r"\bverif(?:y|ication|ication)\b|\btest(?:ing)?\b", SdlcPhase.VERIFICATION.value),
    (r"\bmaintenance\b|\boperations?\b", SdlcPhase.MAINTENANCE.value),
]


def extract_control_id(text: str) -> Optional[str]:
    """Return the first control identifier found in the text, or None."""
    match = CONTROL_ID_RE.search(text)
    return match.group(1).upper() if match else None


def infer_asset_type(text: str, section: str = "") -> str:
    """Deterministic asset_type from keywords in text + section path."""
    combined = f"{section}\n{text}".lower()
    for pattern, asset in ASSET_KEYWORDS:
        if re.search(pattern, combined, re.IGNORECASE):
            return asset
    return AssetType.GENERAL.value


def infer_risk_tier(text: str) -> str:
    """
    Prefer explicit 'Risk Tier: X' statements; fall back to keyword scan.
    """
    # Explicit "Risk Tier: Critical" style (common in baselines)
    explicit = re.search(
        r"risk\s*tier\s*[:\-]\s*(critical|high|medium|low)",
        text,
        re.IGNORECASE,
    )
    if explicit:
        return explicit.group(1).lower()

    combined = text.lower()
    for pattern, tier in RISK_KEYWORDS:
        if re.search(pattern, combined):
            return tier
    return RiskTier.UNSPECIFIED.value


def infer_sdlc_phase(text: str, section: str = "") -> str:
    """
    Prefer explicit 'SDLC Phase: Design' statements; fall back to section
    path and body keywords.
    """
    explicit = re.search(
        r"sdlc\s*phase\s*[:\-]\s*([a-z,\s]+)",
        text,
        re.IGNORECASE,
    )
    if explicit:
        # Take the first phase mentioned
        first = explicit.group(1).split(",")[0].strip().lower()
        for phase in SdlcPhase:
            if phase.value in first:
                return phase.value

    combined = f"{section}\n{text}".lower()
    for pattern, phase in PHASE_KEYWORDS:
        if re.search(pattern, combined):
            return phase
    return SdlcPhase.GENERAL.value


def estimate_token_count(text: str) -> int:
    """Rough token estimate (≈ 4 chars per token). Good enough for lab use."""
    return max(1, len(text) // 4)


def enrich_chunk(
    *,
    text: str,
    section: str,
    doc_type: str,
    source_uri: str,
    chunk_type: str = ChunkType.STANDALONE.value,
    parent_id: Optional[str] = None,
    heading_path: Optional[list[str]] = None,
    source_filename: Optional[str] = None,
    chunk_id: Optional[str] = None,
) -> ChunkRecord:
    """
    Build a fully populated ChunkRecord from raw text + structural context.

    All inference is deterministic and rule-based.
    """
    control_id = extract_control_id(text) or extract_control_id(section)

    record = ChunkRecord(
        chunk_id=chunk_id or str(uuid.uuid4()),
        doc_type=doc_type,
        section=section or "root",
        control_id=control_id,
        asset_type=infer_asset_type(text, section),
        risk_tier=infer_risk_tier(text),
        sdlc_phase=infer_sdlc_phase(text, section),
        source_uri=source_uri,
        parent_id=parent_id,
        chunk_type=chunk_type,
        text=text.strip(),
        token_count=estimate_token_count(text),
        heading_path=heading_path,
        source_filename=source_filename,
    )
    return record


def validate_records(records: list[ChunkRecord]) -> list[str]:
    """
    Return a list of human-readable validation errors.
    Empty list means the corpus is clean.
    """
    errors: list[str] = []
    seen_ids: set[str] = set()

    for i, r in enumerate(records):
        if r.chunk_id in seen_ids:
            errors.append(f"[{i}] duplicate chunk_id: {r.chunk_id}")
        seen_ids.add(r.chunk_id)

        if not r.text.strip():
            errors.append(f"[{i}] empty text (chunk_id={r.chunk_id})")

        if r.chunk_type == ChunkType.CHILD.value and not r.parent_id:
            errors.append(
                f"[{i}] child chunk missing parent_id (chunk_id={r.chunk_id})"
            )

        if r.chunk_type == ChunkType.PARENT.value and r.parent_id is not None:
            errors.append(
                f"[{i}] parent chunk should not have parent_id "
                f"(chunk_id={r.chunk_id})"
            )

    # Check parent references resolve
    id_set = {r.chunk_id for r in records}
    for i, r in enumerate(records):
        if r.parent_id and r.parent_id not in id_set:
            errors.append(
                f"[{i}] parent_id {r.parent_id} does not exist "
                f"(chunk_id={r.chunk_id})"
            )

    return errors
