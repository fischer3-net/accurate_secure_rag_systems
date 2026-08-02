# Lab 4.2 – CI Quality Gate for Evaluation Metrics

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/04-evaluation/notebooks/lab-4.2-ci-gate.ipynb)
[![Open in GitHub](https://img.shields.io/badge/GitHub-notebook-181717?logo=github)](https://github.com/fischer3-net/accurate_secure_rag_systems/blob/main/labs/04-evaluation/notebooks/lab-4.2-ci-gate.ipynb)

*Run in the browser with [Google Colab](../resources/colab.md) or locally via [Docker](../resources/docker.md) / [VS Code](../resources/vscode.md).*

**Objective:** Wire the golden dataset and deterministic evaluation suite into a GitHub Actions (or Cloud Build) pipeline that fails the job when metrics drop below configured thresholds.

---

## Learning Goals

- Express evaluation thresholds in a small config file.
- Run the evaluation suite headlessly in CI.
- Publish a machine-readable metrics report as a build artifact.
- Optionally sketch the equivalent Cloud Build step for GCP-native teams.

---

## Starter Location

```
labs/04-evaluation/
├── src/
│   ├── eval_runner.py         # headless evaluation entrypoint
│   └── thresholds.yaml        # min hit-rate, required fields, …
├── tests/
│   └── test_eval_gate.py      # pytest that enforces thresholds
└── (repo root)
    .github/workflows/eval.yml # quality-gate workflow
```

---

## Pipeline behaviour

```
on: push / pull_request
jobs:
  evaluate:
    steps:
      - checkout
      - setup Python
      - install deps
      - pytest labs/04-evaluation/tests -q
      - python -m src.eval_runner --output metrics.json
      - fail if thresholds missed (pytest gate already does this)
      - upload metrics.json artifact
```

The existing MkDocs deploy workflow remains separate; evaluation should block merge on `main` when gates fail.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| `eval_runner` produces metrics JSON offline | Yes |
| pytest gate fails when a threshold is deliberately lowered | Yes |
| Workflow YAML present and documented | Yes |
| Cloud Build sketch (optional) documented | Yes |

---

## Submission

- Green (or intentionally failing demo) evaluation run in the notebook / local pytest.
- Short note on the thresholds you chose and why.
