"""Unit tests for Lab 3.2 skill router."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.router import SkillRouter, ROUTE_SKILLS
from src.schemas import RouteClass, RouteRequest
from src.registry import build_default_registry


@pytest.fixture
def router():
    return SkillRouter(build_default_registry())


def test_syntax_route(router):
    d = router.decide(RouteRequest(text="Please validate the JSON syntax only", has_dfd=True))
    assert d.route == RouteClass.SYNTAX
    assert d.skill_names == ROUTE_SKILLS[RouteClass.SYNTAX]


def test_structural_route(router):
    d = router.decide(
        RouteRequest(
            text="Does any path from an external entity cross a trust boundary?",
            has_dfd=True,
        )
    )
    assert d.route == RouteClass.STRUCTURAL
    assert "check_trust_boundary_paths" in d.skill_names


def test_policy_route(router):
    d = router.decide(
        RouteRequest(text="Which SEC-DFD controls apply to data stores?", has_dfd=False)
    )
    assert d.route == RouteClass.POLICY
    assert d.skill_names == ["match_security_controls"]


def test_full_route(router):
    d = router.decide(
        RouteRequest(text="Run a full compliance evaluation on this DFD", has_dfd=True)
    )
    assert d.route == RouteClass.FULL
    assert len(d.skill_names) == 4


def test_bare_dfd_defaults_to_full(router):
    d = router.decide(RouteRequest(text="", has_dfd=True))
    assert d.route == RouteClass.FULL


def test_routed_tools_fewer_than_full(router):
    full = router.tool_declarations_for(
        RouteRequest(text="full compliance evaluation", has_dfd=True)
    )
    syntax = router.tool_declarations_for(
        RouteRequest(text="validate syntax only", has_dfd=True)
    )
    assert len(syntax) < len(full)
    assert len(syntax) == 1


def test_token_estimate_shrinks(router):
    reg = router.registry
    full_tokens = reg.estimate_tool_tokens()
    syntax_tokens = reg.estimate_tool_tokens(only=["validate_dfd_syntax"])
    assert syntax_tokens < full_tokens
