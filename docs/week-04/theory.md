# Week 4 Theory – Automated Evaluation & CI/CD

**Focus:** Turning manual “does this look right?” checks into automated, repeatable quality gates that protect the Capstone and every future skill change.

---

## 1. Why Evaluation Is Non-Negotiable for Compliance RAG

A DFD security evaluator that occasionally invents controls or misses a trust-boundary violation is worse than no automation. Security and architecture stakeholders need:

| Guarantee | Metric family |
|-----------|---------------|
| Answers stay inside retrieved policy text | **Faithfulness / Groundedness** |
| Answers actually address the compliance question | **Answer Relevance** |
| The right policy chunks were retrieved | **Context Precision & Context Recall** |
| Structured report fields are present and typed | **Deterministic schema / assertion tests** |

LLM-as-judge metrics (Ragas, Vertex AI Evaluation) are powerful but non-deterministic and cost money. Pair them with **cheap, deterministic checks** that always run in CI.

---

## 2. The RAG Evaluation Triad (applied to DFD compliance)

### Faithfulness / Groundedness
Every claim in the compliance report (control id, risk tier, path finding) must be supportable by retrieved chunks or by a deterministic skill (graph path, syntax check). Hallucinated control ids are automatic failures.

### Answer Relevance
Given “Does this DFD allow an unauthenticated external write to a PII store?”, the report must decide pass/fail/review and cite evidence—not digress into unrelated SDLC phases.

### Context Precision & Context Recall
- **Precision:** Of the chunks retrieved, how many were actually needed?
- **Recall:** Of the ground-truth control passages, how many appeared in the retrieved set?

For this course we also track **hit-rate@k** on control ids (Week 1–2), which is a practical proxy for recall on sparse control libraries.

---

## 3. Deterministic vs. LLM-as-Judge

| Style | Examples | CI role |
|-------|----------|---------|
| **Deterministic** | Schema validation, required fields, control_id ∈ retrieved set, graph path exists, status ∈ {pass,fail,review} | Always-on, free, blocks merge |
| **LLM-as-Judge** | Ragas Faithfulness, Answer Relevancy, Context Precision | Nightly or on-demand; soft gate or report-only unless budget allows |

**Recommended pattern for the Capstone:**

1. Hard gate on deterministic suite (must pass).
2. Soft gate / report on Ragas scores when an API key is present.
3. Thresholds versioned in config (e.g. `min_hit_rate_at_3 = 0.85`).

---

## 4. Golden Datasets

A golden row typically contains:

```json
{
  "id": "G01",
  "question": "…",
  "dfd_fixture": "sample_dfd.json",
  "ground_truth_control_ids": ["SEC-DFD-014"],
  "ground_truth_contexts": ["…excerpt…"],
  "expected_status": "fail",
  "expected_findings_substrings": ["trust-boundary", "external"],
  "notes": "…"
}
```

Lab 4.1 builds ≥20 such rows covering syntax failures, structural violations, clean diagrams, and pure policy questions.

---

## 5. CI/CD Quality Gates

On every push / PR:

```
checkout → install deps → unit tests (Weeks 1–3)
        → evaluation suite (Lab 4)
        → fail job if deterministic thresholds missed
        → publish metrics artifact (JSON + short markdown summary)
```

GitHub Actions (already used for MkDocs deploy) is the path of least resistance for this repo. Cloud Build is documented as the GCP-native equivalent for teams that deploy from Artifact Registry.

---

## 6. Key Takeaways

- Measure both **retrieval quality** and **answer quality**.
- Prefer deterministic gates for security-critical fields.
- Keep a versioned golden set; treat metric regressions like test failures.
- Wire evaluation into the same pipeline that deploys docs and code.

**Next:** Lab 4.1 constructs the golden dataset. Lab 4.2 wires it into CI.
