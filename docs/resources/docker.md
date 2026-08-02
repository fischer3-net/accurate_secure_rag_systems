# Docker / JupyterLab Student Environment

Run every course notebook offline in a consistent Python 3.11 environment without installing packages on your laptop.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) or Docker Engine + Compose (Linux)
- 4 GB free RAM recommended

## Quick start

From the **repository root** (`accurate_secure_rag_systems/`):

```bash
docker compose up --build
```

Open a browser to:

**http://localhost:8888**

Navigate to `labs/01-chunking/notebooks/` (or later weeks) and open any `.ipynb` file.

Stop the environment with `Ctrl+C` in the terminal, or:

```bash
docker compose down
```

## What is mounted

| Host path | Container path | Notes |
|-----------|----------------|-------|
| Repository root | `/home/jovyan/course` | Live bind-mount – saves persist on your machine |
| (Docker volume) | `/home/jovyan/.jupyter` | Jupyter settings / checkpoints |

Edits to notebooks and lab code on the host appear immediately inside the container, and vice versa.

## Lab layout inside Jupyter

```
course/
├── labs/
│   ├── 01-chunking/notebooks/lab-1.1-chunking.ipynb
│   ├── 01-chunking/notebooks/lab-1.2-hybrid-rerank.ipynb
│   ├── 02-storage/notebooks/...
│   ├── 03-skills/notebooks/...
│   └── 04-evaluation/notebooks/...
└── docs/          # MkDocs sources (read-only reference)
```

Each notebook expects to be run with its lab directory as the logical root (the notebooks already adjust `sys.path` for `../src`).

## Running tests from a Jupyter terminal

In JupyterLab: **File → New → Terminal**

```bash
cd labs/01-chunking && pytest tests/ -v
cd ../03-skills && pytest tests/ -v
cd ../04-evaluation && pytest tests/ -v
```

## Optional: Jupyter token

By default the local workshop image starts **without** a login token (convenient on a personal machine).

For shared or remote hosts:

```bash
JUPYTER_TOKEN=choose-a-secret docker compose up --build
```

Then open `http://localhost:8888/?token=choose-a-secret`.

## Optional: live GCP credentials

Notebooks are offline-first. To exercise Vertex AI / BigQuery paths:

```bash
# after gcloud auth application-default login on the host
```

Uncomment the gcloud config volume in `docker-compose.yml`, set `GOOGLE_CLOUD_PROJECT`, and restart.

## Rebuild after dependency changes

If `docker/requirements.txt` changes:

```bash
docker compose build --no-cache
docker compose up
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Port 8888 already in use | `JUPYTER_PORT=8890 docker compose up` |
| Permission errors on Linux | Ensure your user can access the Docker socket; avoid running compose as root for the bind-mount |
| Kernel not found | Kernel `RAG Course (Python 3.11)` is registered on start; pick it in the notebook UI if needed |
| Import errors for `src` | Run notebooks from their lab folder paths as provided; do not move the `.ipynb` files without updating path logic |

## Image details

- Base: `python:3.11-slim-bookworm`
- User: `jovyan` (uid 1000)
- Pre-installed: pydantic, langchain text splitters, JupyterLab, pytest, optional Google Cloud SDKs
- Entrypoint: `docker/entrypoint.sh`
