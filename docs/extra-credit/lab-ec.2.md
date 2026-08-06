# Lab EC.2 – Measuring Fidelity Impact on RAG & Compliance Answers

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/extra-credit/notebooks/lab-ec.2-fidelity-impact.ipynb)
[![Open in GitHub](https://img.shields.io/badge/GitHub-notebook-181717?logo=github)](https://github.com/fischer3-net/accurate_secure_rag_systems/blob/main/labs/extra-credit/notebooks/lab-ec.2-fidelity-impact.ipynb)

*Run in the browser with [Google Colab](../resources/colab.md) or locally via [Docker](../resources/docker.md) / [VS Code](../resources/vscode.md).*

**Objective:** Quantify how controlled losses of structural and semantic fidelity change the answers produced by the existing hybrid retrieval, graph path queries, and scoring skills.

---

## Learning Goals

- Construct paired DFD fixtures (complete vs deliberately lossy).
- Run the same evaluation questions against both versions.
- Record differences in:
  - Path-query results (false negatives / false positives)
  - Retrieved controls (precision / recall of governing controls)
  - Final compliance scores or risk summaries
- Produce a short evidence-based recommendation for how strict the conversion + validation gate should be in a production setting.

---

## Why measure impact?

It is easy to assert that “fidelity matters.” It is more useful to show *how much* it matters for the exact questions your organization cares about. This lab turns the theory into numbers that a security architect or risk owner can act on.

---

## Starter Location (suggested)

```
labs/extra-credit/
├── src/
│   └── fidelity_experiment.py   # harness that runs complete vs lossy side-by-side
├── data/
│   ├── fixtures/
│   │   ├── dfd_complete.json
│   │   ├── dfd_missing_boundary.json
│   │   ├── dfd_missing_classification.json
│   │   └── dfd_missing_flow_attrs.json
│   └── evaluation_questions.json
├── notebooks/
│   └── lab-ec.2-fidelity-impact.ipynb
└── tests/
    └── test_fidelity_impact.py
```

Reuse the graph store, hybrid retriever, and skills from Weeks 2–3 wherever possible. The experiment harness should be thin.

---

## Suggested Experiment Design

1. **Baseline (complete)**  
   Run the full skill pipeline (syntax → paths → policy match → score) on a fully attributed DFD.

2. **Ablations** (one loss at a time)  
   - Remove or omit a TrustBoundary / CROSSES edge  
   - Remove data classification from a sensitive DataStore  
   - Remove authentication / protocol attributes from a cross-boundary flow  
   - Remove provenance metadata (control condition)

3. **Metrics to capture**  
   - Did the path query still detect the known violation?  
   - Which controls were retrieved for the same natural-language question?  
   - Did the final risk / compliance summary change?  
   - Did validation warnings appear?

4. **Report**  
   A small table or notebook section that maps each type of fidelity loss to the observable effect on answers.

---

## Implementation Notes

A minimal side-by-side experiment harness is sketched in the [Theory – Recommended Python Building Blocks](theory.md#7-recommended-python-building-blocks) section (`run_fidelity_ablation`). Wire it to the existing graph path query and hybrid retrieval functions from Weeks 2–3 so the comparison stays consistent with the rest of the course.

Recommended ablation order:

1. Structural – remove a `CROSSES` edge or TrustBoundary node  
2. Semantic – strip `classification` / `trust_level` from a sensitive DataStore  
3. Flow attributes – remove `protocol` / authentication flags from a cross-boundary flow  

Record both the validation issues and the downstream answer differences for each ablation.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| At least three controlled ablations are executed | Yes |
| Path-query false-negative behavior is demonstrated for structural loss | Yes |
| Change in retrieved controls or score is shown for semantic loss | Yes |
| Notebook contains a clear comparison table | Yes |
| Short written recommendation on validation strictness | Yes |

---

## Validation Checklist

- [ ] Complete and lossy fixtures are checked into the repo
- [ ] Experiment harness is deterministic and offline-capable
- [ ] Results are recorded in a form that can be re-run in CI
- [ ] Recommendation explicitly links observed impact back to the theory taxonomy (structural vs semantic)
