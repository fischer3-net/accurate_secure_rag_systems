"""Tests for Lab 2.2 graph schema, path finding, and GraphRAG."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.graph_schema import load_dfd_json
from src.graph_store import DfdGraphStore
from src.graph_rag import GraphRAG


@pytest.fixture(scope="module")
def dfd_path():
    return ROOT / "data" / "sample_dfd.json"


@pytest.fixture(scope="module")
def graph(dfd_path):
    doc = load_dfd_json(dfd_path)
    g = DfdGraphStore()
    g.ingest(doc)
    return g


def test_sample_dfd_loads(dfd_path):
    doc = load_dfd_json(dfd_path)
    assert len(doc.nodes) >= 4
    assert len(doc.edges) >= 3
    assert doc.validate() == []


def test_graph_summary(graph):
    s = graph.summary()
    assert s["nodes"] >= 4
    assert s["flow_edges"] >= 1


def test_find_external_to_datastore_paths(graph):
    paths = graph.find_paths(
        source_type="ExternalEntity",
        target_type="DataStore",
        require_crosses_trust_boundary=True,
    )
    assert len(paths) >= 1
    assert any(p.crosses_trust_boundary for p in paths)


def test_control_links_present(graph):
    assert graph.control_links.get("ee_partner")
    assert "SEC-DFD-014" in graph.control_links["ee_partner"]


def test_link_controls_from_corpus(graph, week1_corpus):
    before = sum(len(v) for v in graph.control_links.values())
    added = graph.link_controls_from_corpus(week1_corpus)
    after = sum(len(v) for v in graph.control_links.values())
    assert added >= 0
    assert after >= before


def test_graph_rag_ask(graph):
    grag = GraphRAG(graph=graph, retriever=None)
    answer = grag.ask("Are there flows from external entities into PII stores?")
    assert answer.structural_findings
    assert isinstance(answer.policy_hits, list)
