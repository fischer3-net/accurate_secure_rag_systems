"""
Dynamic Skill Router for Lab 3.2.

Classifies a request with auditable heuristics and returns the minimal
skill subset to expose or invoke.
"""

from __future__ import annotations

import re
from typing import Optional

from .registry import SkillRegistry, build_default_registry
from .schemas import RouteClass, RouteDecision, RouteRequest


# Keyword signals (kept simple and reviewable)
_SYNTAX_HINTS = re.compile(
    r"\b(validat(?:e|ion)|syntax|well-?formed|schema only|just check (the )?json)\b",
    re.I,
)
_STRUCTURAL_HINTS = re.compile(
    r"\b(path|trust\s*boundar|cross(?:es|ing)?|external\s+entit|data\s*store|connectivity|reach)\b",
    re.I,
)
_POLICY_HINTS = re.compile(
    r"\b(control|policy|baseline|SEC-DFD|requirement|which controls?)\b",
    re.I,
)
_FULL_HINTS = re.compile(
    r"\b(evaluat|compliance|full (review|assessment)|score|overall|end-?to-?end)\b",
    re.I,
)

ROUTE_SKILLS: dict[RouteClass, list[str]] = {
    RouteClass.SYNTAX: ["validate_dfd_syntax"],
    RouteClass.STRUCTURAL: [
        "validate_dfd_syntax",
        "check_trust_boundary_paths",
    ],
    RouteClass.POLICY: ["match_security_controls"],
    RouteClass.FULL: [
        "validate_dfd_syntax",
        "check_trust_boundary_paths",
        "match_security_controls",
        "score_sdlc_compliance",
    ],
}


class SkillRouter:
    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or build_default_registry()

    def classify(self, request: RouteRequest | dict) -> RouteClass:
        if isinstance(request, dict):
            request = RouteRequest.model_validate(request)
        text = request.text or ""

        # Explicit full evaluation wins when a DFD is present + evaluation language
        if request.has_dfd and _FULL_HINTS.search(text):
            return RouteClass.FULL
        if request.has_dfd and not text.strip():
            # Bare DFD upload → full evaluation by default
            return RouteClass.FULL

        # Specific intents
        if _SYNTAX_HINTS.search(text) and not (
            _STRUCTURAL_HINTS.search(text) or _POLICY_HINTS.search(text)
        ):
            return RouteClass.SYNTAX
        if _STRUCTURAL_HINTS.search(text) and not _POLICY_HINTS.search(text):
            return RouteClass.STRUCTURAL
        if _POLICY_HINTS.search(text) and not request.has_dfd:
            return RouteClass.POLICY
        if _POLICY_HINTS.search(text) and request.has_dfd:
            return RouteClass.FULL
        if _FULL_HINTS.search(text):
            return RouteClass.FULL
        if request.has_dfd:
            return RouteClass.STRUCTURAL
        if _POLICY_HINTS.search(text):
            return RouteClass.POLICY

        # Safe default for free-text with no DFD: policy lookup
        return RouteClass.POLICY

    def select(self, route: RouteClass) -> list[str]:
        return list(ROUTE_SKILLS[route])

    def decide(self, request: RouteRequest | dict) -> RouteDecision:
        if isinstance(request, dict):
            request = RouteRequest.model_validate(request)
        route = self.classify(request)
        skills = self.select(route)
        rationale = (
            f"has_dfd={request.has_dfd}; "
            f"text_len={len(request.text or '')}; "
            f"route={route.value}"
        )
        return RouteDecision(route=route, skill_names=skills, rationale=rationale)

    def tool_declarations_for(self, request: RouteRequest | dict) -> list[dict]:
        decision = self.decide(request)
        return self.registry.vertex_tool_declarations(only=decision.skill_names)
