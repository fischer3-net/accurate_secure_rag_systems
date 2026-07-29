# Capstone Project – Automated DFD Security & SDLC Compliance Evaluator

Students will work in teams or individually to build a complete, production-ready pipeline on GCP using Python.

## High-Level Goal

Given a structured representation (JSON / XML / Mermaid) of a Data Flow Diagram, the system must:

1. Retrieve and reason over the relevant SDLC handbook sections and security baselines.
2. Apply modular skills for syntax validation, control matching, and compliance scoring.
3. Return a structured JSON report containing pass/fail controls, risk ratings, and precise references.
4. Pass an automated test suite demonstrating >90% precision and groundedness.

## Recommended Architecture

- Hybrid storage (e.g., AlloyDB pgvector for rules + optional graph for connectivity).
- Dynamic skill router from Week 3.
- Evaluation suite from Week 4 integrated as a CI quality gate.

## Next Pages

- [Detailed Requirements](requirements.md)
- [Starter Template Guidance](starter.md)
