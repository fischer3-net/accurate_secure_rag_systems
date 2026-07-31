# Lab 03 – Skill Architecture & Dynamic Routing

Starter implementation for **Lab 3.1** (modular Pydantic skills) and **Lab 3.2** (dynamic skill router).

## Layout

```
03-skills/
├── src/
│   ├── schemas.py
│   ├── skills_syntax.py
│   ├── skills_graph.py
│   ├── skills_policy.py
│   ├── skills_score.py
│   ├── registry.py
│   ├── router.py
│   └── mega_prompt.py          # anti-pattern baseline
├── data/
│   ├── sample_dfd.json
│   └── rag_chunks.jsonl
├── notebooks/
│   ├── lab-3.1-modular-skills.ipynb
│   └── lab-3.2-skill-router.ipynb
└── tests/
```

## Quick start

```bash
cd labs/03-skills
pip install pydantic pytest
pytest tests/ -v
jupyter notebook notebooks/lab-3.1-modular-skills.ipynb
```

Skills are deterministic where possible (syntax, graph, scoring). Policy matching uses the Week 1 corpus offline and can swap in the Week 1 `HybridRetriever` later.
