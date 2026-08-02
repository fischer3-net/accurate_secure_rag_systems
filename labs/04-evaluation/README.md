# Lab 04 – Automated Evaluation & CI Quality Gates

Starter implementation for **Lab 4.1** (golden dataset) and **Lab 4.2** (CI evaluation gate).

## Layout

```
04-evaluation/
├── data/
│   ├── golden_dataset.jsonl      # 22 golden rows
│   ├── fixtures/                 # DFD variants
│   └── rag_chunks.jsonl          # Week 1 corpus export
├── src/
│   ├── dataset.py
│   ├── metrics.py
│   ├── eval_runner.py
│   └── thresholds.yaml
├── notebooks/
│   ├── lab-4.1-golden-dataset.ipynb
│   └── lab-4.2-ci-gate.ipynb
├── scripts/
│   └── cloudbuild-eval.yaml
└── tests/
```

Repo root also includes `.github/workflows/eval.yml`.

## Quick start

```bash
cd labs/04-evaluation
pip install pydantic pytest
pytest tests/ -v
python -c "from src.eval_runner import main; raise SystemExit(main(['--output','output/metrics.json']))"
```

## Metrics (deterministic)

- **control hit-rate** – fraction of ground-truth control ids recovered
- **status match** – expected vs actual overall status (pass/fail/review)
- **findings substring score** – expected phrases present in findings
- **overall** – weighted combination used as the primary CI gate

Optional Ragas / Vertex LLM-judge metrics can be added later without changing the hard gate.
