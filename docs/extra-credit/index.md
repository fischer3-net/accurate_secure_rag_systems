# Extra Credit – DFD Fidelity, Canonical Models & RAG Implications

**Focus:** Understanding and mitigating the fidelity issues that arise when converting visual Data Flow Diagrams into structured representations for RAG-based security and SDLC evaluation.

## Learning Outcomes

By completing this extra-credit module you will be able to:

- Distinguish visual, structural, semantic, and provenance fidelity—and know which losses actually matter for compliance evaluation.
- Explain how incompleteness in a structured DFD propagates into retrieval, graph path queries, skills, and final evaluation metrics.
- Design a canonical DFD JSON schema and a validation skill that surface missing security-relevant information rather than silently ignoring it.
- Measure the impact of controlled fidelity loss on the answers produced by the existing hybrid + graph + skill pipeline.

## Agenda

1. Theory – Taxonomy of fidelity loss and its implications for RAG systems
2. Lab EC.1 – Canonical DFD schema, validation skill, and controlled conversion patterns
3. Lab EC.2 – Measuring fidelity impact on retrieval, path queries, and compliance scores

## Prerequisites

- Completed Weeks 1–3 (chunking, hybrid/graph storage, modular skills)
- Familiarity with the sample DFD JSON and graph schema from Lab 2.2
- Optional but recommended: Week 4 evaluation concepts

## Navigation

- [Theory](theory.md)
- [Lab EC.1 – Canonical Schema & Validation](lab-ec.1.md)
- [Lab EC.2 – Measuring Fidelity Impact](lab-ec.2.md)
