# Week 4 – Automated Accuracy Testing, Evaluation Metrics & Continuous Integration

**Focus:** Moving from manual spot-checks to automated, continuous accuracy, security, and performance testing pipelines.

## Learning Outcomes

- Define and measure Faithfulness / Groundedness, Answer Relevance, Context Precision, and Context Recall for the DFD compliance use case.
- Construct synthetic golden datasets from security handbooks.
- Integrate Ragas (and optionally Vertex AI Evaluation) into a `pytest` suite.
- Wire the evaluation suite into Cloud Build / GitHub Actions as a quality gate (e.g., block merge if Faithfulness < 92%).

## Agenda

1. Theory – Evaluation triad, deterministic vs. LLM-as-judge, CI/CD patterns
2. Lab 4.1 – Golden dataset for 20 sample DFD evaluations
3. Lab 4.2 – Cloud Build pipeline that runs Ragas on every push

## Navigation

- [Theory](theory.md)
- [Lab 4.1](lab-4.1.md)
- [Lab 4.2](lab-4.2.md)
