"""Week 3 – modular skills and dynamic router."""

from .schemas import (
    ValidateDfdInput,
    ValidateDfdOutput,
    CheckTrustPathsInput,
    CheckTrustPathsOutput,
    MatchControlsInput,
    MatchControlsOutput,
    ScoreComplianceInput,
    ScoreComplianceOutput,
    RouteClass,
    RouteRequest,
    RouteDecision,
    ComplianceStatus,
)
from .skills_syntax import validate_dfd_syntax
from .skills_graph import check_trust_boundary_paths
from .skills_policy import match_security_controls, set_policy_corpus, ControlCorpus
from .skills_score import score_sdlc_compliance
from .registry import SkillRegistry, build_default_registry
from .router import SkillRouter
from .mega_prompt import mega_prompt_evaluate, mega_prompt_token_estimate

__all__ = [
    "validate_dfd_syntax",
    "check_trust_boundary_paths",
    "match_security_controls",
    "score_sdlc_compliance",
    "SkillRegistry",
    "build_default_registry",
    "SkillRouter",
    "mega_prompt_evaluate",
    "mega_prompt_token_estimate",
    "set_policy_corpus",
    "ControlCorpus",
    "RouteClass",
    "RouteRequest",
    "RouteDecision",
    "ComplianceStatus",
]
