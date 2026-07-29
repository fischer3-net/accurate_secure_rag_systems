# Week 4 Theory – Automated Evaluation & CI/CD

!!! note "Status"
    Skeleton. Expand with metric definitions, example Ragas configurations, and Cloud Build YAML patterns.

## The RAG Evaluation Triad

- **Faithfulness / Groundedness** – Does the answer stay strictly within the retrieved SDLC/security context?
- **Answer Relevance** – Does the evaluation actually answer whether the DFD complies?
- **Context Precision & Context Recall** – Quality of the retrieved chunks versus ground-truth requirements.

## Building the Evaluation Suite

- Ragas, TruLens, Vertex AI Rapid Evaluation API.
- Synthetic golden datasets (Questions, Ground-Truth contexts, Expected outputs).
- Deterministic assertions vs. LLM-as-a-Judge.

## CI/CD Integration

- Cloud Build / GitHub Actions regression tests on prompt changes, embedding upgrades, and new skills.
- Quality gates that block deployment when metrics drop below defined thresholds.
