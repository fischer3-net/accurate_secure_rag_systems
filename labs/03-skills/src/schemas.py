"""
Shared Pydantic models for Week 3 skills and Capstone-style reports.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# DFD payload (aligned with Week 2 sample_dfd.json)
# ---------------------------------------------------------------------------

class DfdNodeIn(BaseModel):
    id: str
    type: str
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)


class DfdEdgeIn(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class DfdDocumentIn(BaseModel):
    name: str = "unnamed"
    description: str = ""
    nodes: list[DfdNodeIn]
    edges: list[DfdEdgeIn]


# ---------------------------------------------------------------------------
# Skill I/O
# ---------------------------------------------------------------------------

class SyntaxIssue(BaseModel):
    severity: str  # error | warning
    code: str
    message: str
    path: Optional[str] = None


class ValidateDfdInput(BaseModel):
    dfd: DfdDocumentIn


class ValidateDfdOutput(BaseModel):
    ok: bool
    issues: list[SyntaxIssue] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0


class TrustPathFinding(BaseModel):
    path: list[str]
    crosses_trust_boundary: bool
    governed_control_ids: list[str] = Field(default_factory=list)


class CheckTrustPathsInput(BaseModel):
    dfd: DfdDocumentIn
    require_crosses_trust_boundary: bool = True


class CheckTrustPathsOutput(BaseModel):
    path_count: int
    paths: list[TrustPathFinding] = Field(default_factory=list)
    summary: str = ""


class MatchControlsInput(BaseModel):
    query: str
    top_k: int = 5
    asset_type: Optional[str] = None
    risk_tier: Optional[str] = None


class MatchedControl(BaseModel):
    control_id: Optional[str] = None
    section: Optional[str] = None
    score: float = 0.0
    text_preview: str = ""


class MatchControlsOutput(BaseModel):
    query: str
    matches: list[MatchedControl] = Field(default_factory=list)


class ComplianceStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    REVIEW = "review"
    UNKNOWN = "unknown"


class ControlResult(BaseModel):
    control_id: str
    status: ComplianceStatus
    rationale: str = ""


class ScoreComplianceInput(BaseModel):
    syntax: Optional[ValidateDfdOutput] = None
    trust_paths: Optional[CheckTrustPathsOutput] = None
    policy_matches: Optional[MatchControlsOutput] = None


class ScoreComplianceOutput(BaseModel):
    overall_status: ComplianceStatus
    control_results: list[ControlResult] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    risk_summary: str = ""


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

class RouteClass(str, Enum):
    SYNTAX = "syntax"
    STRUCTURAL = "structural"
    POLICY = "policy"
    FULL = "full"


class RouteRequest(BaseModel):
    """What the router sees – text intent and/or a DFD payload."""
    text: str = ""
    has_dfd: bool = False
    dfd_name: Optional[str] = None


class RouteDecision(BaseModel):
    route: RouteClass
    skill_names: list[str]
    rationale: str = ""
