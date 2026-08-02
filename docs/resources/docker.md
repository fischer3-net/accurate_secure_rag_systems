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

### Upgrading from the earlier `jovyan` image

If you previously started the stack under the old `jovyan` user, clear the old volumes once so ownership is recreated:

```bash
docker compose down -v
docker compose up --build
```

## What is mounted

| Host path | Container path | Notes |
|-----------|----------------|-------|
| Repository root | `/home/fischer3/course` | Live bind-mount – saves persist on your machine |
| (Docker volume) | `/home/fischer3/.jupyter` | Jupyter config (ownership fixed at start) |
| (Docker volume) | `/home/fischer3/.local` | Jupyter data / kernels |

Edits to notebooks and lab code on the host appear immediately inside the container, and vice versa.

The container user is **`fischer3`** (uid 1000). The entrypoint runs briefly as root to `chown` the Jupyter volumes (which Docker creates as root), then drops privileges with `gosu`.

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

Notebooks are offline-first. To exercise Vertex AI / BigQuery paths, after `gcloud auth application-default login` on the host, uncomment the gcloud config volume in `docker-compose.yml`, set `GOOGLE_CLOUD_PROJECT`, and restart.

## Rebuild after dependency changes

If `docker/requirements.txt` changes:

```bash
docker compose build --no-cache
docker compose up
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `PermissionError: ... /.jupyter/migrated` | `docker compose down -v` then `docker compose up --build` |
| Port 8888 already in use | `JUPYTER_PORT=8890 docker compose up` |
| Permission errors on Linux bind-mount | Ensure your host user can write the repo; container uid is 1000 |
| Kernel not found | Kernel `RAG Course (Python 3.11)` is registered on start |
| Import errors for `src` | Run notebooks from their lab folder paths as provided |

## Image details

- Base: `python:3.11-slim-bookworm`
- User: `fischer3` (uid 1000)
- Pre-installed: pydantic, langchain text splitters, JupyterLab, pytest, optional Google Cloud SDKs
- Entrypoint: `docker/entrypoint.sh` (fixes volume ownership → `gosu fischer3` → JupyterLab)
- Default command: `jupyter lab`

## VS Code on the host

To use Visual Studio Code against this container (Dev Containers or Attach), see [VS Code + Container Workflow](vscode.md).
