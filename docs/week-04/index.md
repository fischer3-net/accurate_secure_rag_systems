# Week 4 – Automated Accuracy Testing, Evaluation Metrics & Continuous Integration

**Focus:** Moving from manual spot-checks to automated, continuous accuracy, security, and performance testing pipelines.

## Learning Outcomes

- Define and measure Faithfulness / Groundedness, Answer Relevance, Context Precision, and Context Recall for the DFD compliance use case.
- Construct synthetic golden datasets from security handbooks and DFD fixtures.
- Run deterministic evaluation metrics offline and optionally layer LLM-as-judge scores.
- Wire the evaluation suite into GitHub Actions (or Cloud Build) as a quality gate.

## Agenda

1. Theory – Evaluation triad, deterministic vs. LLM-as-judge, CI/CD patterns
2. Lab 4.1 – Golden dataset (≥20 DFD evaluation rows)
3. Lab 4.2 – CI pipeline that runs evaluation on every relevant push

## Navigation

- [Theory](theory.md)
- [Lab 4.1 – Golden Dataset](lab-4.1.md)
- [Lab 4.2 – CI Quality Gate](lab-4.2.md)
