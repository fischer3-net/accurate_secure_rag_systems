# Lab 4.1 – Ground-Truth Benchmark Dataset for DFD Evaluations

**Objective:** Build a golden dataset of ≥20 DFD security evaluation examples that the automated suite (and the Capstone) can score against.

---

## Learning Goals

- Design golden rows with questions, ground-truth control ids, expected status, and optional context excerpts.
- Cover diverse cases: clean diagrams, syntax errors, trust-boundary violations, pure policy lookups.
- Load the dataset in pytest and in a notebook for manual inspection.
- Document coverage gaps so Capstone teams can extend the set.

---

## Dataset schema

Each row (JSONL) must include at least:

| Field | Description |
|-------|-------------|
| `id` | Stable identifier (`G01` …) |
| `question` | Natural-language evaluation question |
| `dfd_fixture` | Filename under `data/fixtures/` or `null` for policy-only |
| `ground_truth_control_ids` | List of control ids that should surface |
| `expected_status` | `pass` \| `fail` \| `review` \| `n/a` |
| `expected_findings_substrings` | Substrings that should appear in findings (optional) |
| `ground_truth_contexts` | Short policy excerpts (optional, for Ragas) |
| `tags` | e.g. `["structural", "trust_boundary"]` |
| `notes` | Author rationale |

---

## Starter Location

```
labs/04-evaluation/
├── data/
│   ├── golden_dataset.jsonl      # ≥20 rows
│   └── fixtures/                 # small DFD JSON variants
├── src/
│   ├── dataset.py                # loader + validation
│   └── metrics.py                # deterministic scorers
├── notebooks/
│   └── lab-4.1-golden-dataset.ipynb
└── tests/
    └── test_dataset.py
```

---

## Step-by-Step

1. Review the provided golden rows and fixtures.
2. Add at least two new rows (one structural, one policy-only) following the schema.
3. Run `validate_golden_dataset()` – all rows must pass.
4. Execute deterministic metrics against the Week 3 skills on a subset of rows.
5. Note coverage gaps for the Capstone.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| ≥ 20 golden rows | Yes |
| Schema validation passes for every row | Yes |
| At least 3 fixtures (clean / violation / syntax-error) | Yes |
| Deterministic metrics runnable offline | Yes |

---

## Submission

Updated `golden_dataset.jsonl` (if you added rows) + notebook showing metric results on a sample of rows.
