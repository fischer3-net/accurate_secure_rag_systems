# Capstone Starter Template Guidance

You already have working building blocks from Weeks 1–4. Assemble them into a single evaluator rather than rewriting from scratch.

## Reuse map

| Capstone need | Course artefact |
|---------------|-----------------|
| Document-aware chunks + metadata | `labs/01-chunking` |
| Hybrid retrieval / RRF | `labs/01-chunking/src/retrieval.py` |
| Storage abstraction | `labs/02-storage` (`PgVectorStore`, graph) |
| Modular skills + router | `labs/03-skills` |
| Golden dataset + CI gate | `labs/04-evaluation` |

## Suggested student project layout

```
dfd-compliance-evaluator/
├── src/
│   ├── skills/          # from Week 3 (or thin wrappers)
│   ├── router/
│   ├── retrieval/
│   ├── storage/
│   └── evaluation/
├── data/
│   ├── policies/
│   ├── fixtures/
│   └── golden_dataset.jsonl
├── tests/
├── scripts/ or terraform/
├── .github/workflows/eval.yml
└── README.md
```

## Minimum acceptance path

1. Ingest policy docs → enriched corpus (Week 1).
2. Index with chosen store (Week 2) and justify the choice.
3. Route DFD input through modular skills (Week 3).
4. Emit structured `ScoreComplianceOutput`-style JSON.
5. Pass `labs/04-evaluation` deterministic gates (or an extended golden set) at the Capstone thresholds (>90% precision / groundedness on your suite).

## Tips

- Keep syntax and graph skills deterministic.
- Treat DFD JSON as untrusted input.
- Version thresholds in config; do not hard-code magic numbers in CI YAML only.
