# Running Labs in VS Code with the Course Container

Use **Visual Studio Code on your host** while the Python environment, dependencies, and lab files run **inside the Docker container**. Edits save to your local disk via the bind mount—no package installs on the host required.

There are two supported workflows:

| Workflow | Best when… |
|----------|------------|
| **A. Dev Containers** (“Reopen in Container”) | You want the full IDE (terminal, debugger, tests, notebooks) inside the course image |
| **B. Attach to running Compose** | You already started `docker compose up` for JupyterLab and want VS Code alongside it |

---

## Prerequisites

1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) or Docker Engine + Compose (Linux)
2. [Visual Studio Code](https://code.visualstudio.com/)
3. VS Code extensions:
   - **Dev Containers** (`ms-vscode-remote.remote-containers`)
   - **Python** (`ms-python.python`)
   - **Jupyter** (`ms-toolsai.jupyter`) — for `.ipynb` support

On Windows, keep the repo on the Linux filesystem if you use WSL2 (e.g. `\\wsl$\Ubuntu\home\…`) for better bind-mount performance.

---

## Workflow A — Dev Containers (recommended)

This uses the repo’s `.devcontainer/` config and the same Dockerfile as the Jupyter stack.

### Steps

1. Clone or unzip the course repository and open the **repository root** in VS Code:

   ```bash
   code accurate_secure_rag_systems
   ```

2. When prompted **“Reopen in Container”**, accept it.  
   Or: Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → **Dev Containers: Reopen in Container**.

3. VS Code builds the image (first time only), then reloads the window connected as user `fischer3`.

4. Open a lab notebook, e.g.:

   ```
   labs/01-chunking/notebooks/lab-1.1-chunking.ipynb
   ```

5. Select the kernel **RAG Course (Python 3.11)** or the default Python 3.11 interpreter inside the container.

6. Run cells with **Shift+Enter**.

### Integrated terminal

**Terminal → New Terminal** opens a shell **inside** the container:

```bash
whoami                    # fischer3
pwd                       # /home/fischer3/course  (or workspace folder)
cd labs/01-chunking && pytest tests/ -v
```

### Stop / rebuild

- Command Palette → **Dev Containers: Reopen Folder Locally** (leave the container)
- **Dev Containers: Rebuild Container** after changes to `docker/requirements.txt` or the Dockerfile

---

## Workflow B — Attach to a running `docker compose` container

Use this if JupyterLab is already up at http://localhost:8888 and you also want VS Code.

### Steps

1. From the repo root on the host:

   ```bash
   docker compose up --build -d
   ```

2. In VS Code: Command Palette → **Dev Containers: Attach to Running Container…**  
   Select **`rag-course-jupyter`**.

3. When the new window opens, choose **Open Folder** → `/home/fischer3/course`.

4. Install the Python and Jupyter extensions **in the container** if VS Code prompts you (they run on the remote side).

5. Open notebooks under `labs/…/notebooks/` and select the container’s Python 3.11 kernel.

You can use JupyterLab in the browser and VS Code at the same time; both see the same bind-mounted files.

### Detach

Close the attached VS Code window. Stop Compose when finished:

```bash
docker compose down
```

---

## Where files live

| Location | Meaning |
|----------|---------|
| Host: your clone of the repo | Source of truth on disk |
| Container: `/home/fischer3/course` | Same files (bind mount) |
| Container: `/home/fischer3/.jupyter` | Jupyter config (Docker volume) |

Saving a notebook in VS Code writes through to the host immediately.

---

## Running tests from VS Code

**Option 1 — terminal**

```bash
cd labs/03-skills && pytest tests/ -v
cd ../04-evaluation && pytest tests/ -v
```

**Option 2 — Testing UI**

1. Install/enable the Python extension in the container.
2. Command Palette → **Python: Configure Tests** → `pytest` → select the lab’s `tests` folder (or run from each lab directory).

---

## Optional: live GCP from VS Code

Notebooks are offline-first. For Vertex AI / BigQuery paths:

1. On the host: `gcloud auth application-default login`
2. Uncomment the gcloud config volume in `docker-compose.yml` (or add the same mount under `mounts` in `.devcontainer/devcontainer.json`)
3. Set `GOOGLE_CLOUD_PROJECT` in the container environment
4. Rebuild / restart the container

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| “Reopen in Container” missing | Install the **Dev Containers** extension |
| Permission errors on `.jupyter` | `docker compose down -v` then rebuild / reopen |
| Wrong Python interpreter | Status bar → select `/usr/local/bin/python` (container) |
| Notebook kernel won’t start | Kernel picker → **Python 3.11** / **RAG Course (Python 3.11)** |
| Windows path / performance issues | Clone the repo inside WSL2 and open it from there |
| Extensions missing after attach | Install Python + Jupyter into **container** when prompted |
| Port 8888 in use | Only needed for browser JupyterLab; pure Dev Containers does not require publishing 8888 |

---

## Related

- [Docker / JupyterLab Environment](docker.md) — browser-only JupyterLab via Compose  
- [Recommended Tooling](tooling.md)
