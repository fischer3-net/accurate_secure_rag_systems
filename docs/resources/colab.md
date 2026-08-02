# Running Labs in Google Colab

Use Google Colab when you do not want to install Docker or a local Python stack. Each lab notebook can be opened with one click via the **Open in Colab** badge on the lab pages.

**Repository:** [fischer3-net/accurate_secure_rag_systems](https://github.com/fischer3-net/accurate_secure_rag_systems)

---

## Open a notebook in Colab

| Lab | Notebook | Launch |
|-----|----------|--------|
| 1.1 Chunking & Metadata | `lab-1.1-chunking.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/01-chunking/notebooks/lab-1.1-chunking.ipynb) |
| 1.2 Hybrid Retrieval | `lab-1.2-hybrid-rerank.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/01-chunking/notebooks/lab-1.2-hybrid-rerank.ipynb) |
| 2.1 Storage Benchmark | `lab-2.1-benchmark.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/02-storage/notebooks/lab-2.1-benchmark.ipynb) |
| 2.2 Graph-Augmented RAG | `lab-2.2-graph-rag.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/02-storage/notebooks/lab-2.2-graph-rag.ipynb) |
| 3.1 Modular Skills | `lab-3.1-modular-skills.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/03-skills/notebooks/lab-3.1-modular-skills.ipynb) |
| 3.2 Skill Router | `lab-3.2-skill-router.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/03-skills/notebooks/lab-3.2-skill-router.ipynb) |
| 4.1 Golden Dataset | `lab-4.1-golden-dataset.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/04-evaluation/notebooks/lab-4.1-golden-dataset.ipynb) |
| 4.2 CI Quality Gate | `lab-4.2-ci-gate.ipynb` | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/fischer3-net/accurate_secure_rag_systems/blob/main/labs/04-evaluation/notebooks/lab-4.2-ci-gate.ipynb) |

The badge opens the notebook from the `main` branch on GitHub. If your fork uses another branch or org name, change the URL accordingly.

---

## First-time setup in Colab

Notebooks include a **Colab bootstrap** cell near the top. Run it first. It will:

1. Clone this repository into `/content/accurate_secure_rag_systems` (if needed)
2. Change into the correct lab directory
3. Install lightweight offline dependencies (`pydantic`, `langchain-text-splitters`, `pytest`, …)
4. Put the lab `src/` package on `sys.path`

If a notebook is older and missing that cell, paste this at the top and set `LAB_DIR` for the lab you are running:

```python
# --- Colab bootstrap (paste if missing) ---
import os, sys
from pathlib import Path

REPO_URL = "https://github.com/fischer3-net/accurate_secure_rag_systems.git"
REPO_ROOT = Path("/content/accurate_secure_rag_systems")
LAB_DIR = "labs/01-chunking"  # change per lab: 02-storage, 03-skills, 04-evaluation

if not REPO_ROOT.exists():
    !git clone --depth 1 {REPO_URL} {REPO_ROOT}

LAB = REPO_ROOT / LAB_DIR
os.chdir(LAB)
sys.path.insert(0, str(LAB))
# Week 2+ may also need Week 1 on the path:
sys.path.insert(0, str(REPO_ROOT / "labs" / "01-chunking"))

%pip install -q pydantic python-dotenv langchain-text-splitters langchain-core pytest pyyaml pandas

print("LAB =", LAB)
print("cwd =", Path.cwd())
```

Then run the remaining cells as usual.

---

## What works offline in Colab

| Feature | Colab without GCP | Notes |
|---------|-------------------|--------|
| Document-aware chunking, metadata | Yes | Lab 1.1 |
| Hybrid BM25 + dense + RRF | Yes | Lab 1.2 (hashing embedder fallback) |
| Storage benchmark / graph RAG | Yes | In-memory stores |
| Skills + router | Yes | Deterministic skills |
| Golden dataset + eval gate | Yes | Lab 4 |
| Live Vertex AI / BigQuery writes | Optional | Requires GCP project + auth |

Optional GCP in Colab:

```python
from google.colab import auth
auth.authenticate_user()
!gcloud config set project YOUR_PROJECT_ID
```

---

## Saving your work

- **Copy to Drive:** Colab menu → *File → Save a copy in Drive*
- **Download:** *File → Download → .ipynb*
- Changes in `/content/...` are **not** pushed back to GitHub unless you configure git credentials and push from a cell

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: src` | Re-run the bootstrap cell; confirm `LAB` points at the lab folder that contains `src/` |
| `FileNotFoundError` for `data/...` | Bootstrap must `os.chdir(LAB)` so relative `data/` paths resolve |
| Badge 404 | Repo must be **public** (or you must be logged into GitHub with access); path must match `main` |
| Private fork | Open Colab → *File → Upload notebook*, or use a GitHub token to clone your fork URL in the bootstrap cell |
| Kernel restart | Re-run the bootstrap cell before other cells |

---

## Related

- [Docker / JupyterLab Environment](docker.md)
- [VS Code + Container Workflow](vscode.md)
