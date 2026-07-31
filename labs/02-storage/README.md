# Lab 02 – Storage Architecture & Graph-Augmented RAG

Starter implementation for **Lab 2.1** (hybrid vs pure vector stores) and **Lab 2.2** (DFD graph + Graph RAG).

## Layout

```
02-storage/
├── src/
│   ├── store_base.py
│   ├── pgvector_store.py          # AlloyDB-style hybrid (offline)
│   ├── vector_search_store.py     # Vector Search-style pure semantic (offline)
│   ├── benchmark.py
│   ├── graph_schema.py
│   ├── graph_store.py
│   └── graph_rag.py
├── data/sample_dfd.json
├── notebooks/
│   ├── lab-2.1-benchmark.ipynb
│   └── lab-2.2-graph-rag.ipynb
├── scripts/
│   ├── provision_alloydb.md
│   └── provision_vector_search.md
└── tests/
```

## Quick start

```bash
cd labs/02-storage
pip install -r ../01-chunking/requirements.txt   # shared deps
pytest tests/ -v
jupyter notebook notebooks/lab-2.1-benchmark.ipynb
jupyter notebook notebooks/lab-2.2-graph-rag.ipynb
```

Both labs reuse the Week 1 corpus and evaluation queries via relative imports.
