# Testing & Runtime Environments

Central index of every supported way to run the course labs and documentation.  
Use this page to choose an environment; follow the linked detailed guide for full setup steps.

As new options are added they will appear here first.

---

## Current options at a glance

| Environment | Best for | Offline? | Live GCP? | Detailed guide |
|-------------|----------|----------|-----------|----------------|
| **Docker + JupyterLab** | Running all lab notebooks consistently | Yes | Optional (ADC) | [docker.md](docker.md) |
| **VS Code Dev Containers** | Full IDE (editor, debugger, terminal, notebooks) inside the course image | Yes | Optional (ADC) | [vscode.md](vscode.md) |
| **VS Code attach to Compose** | JupyterLab already running + VS Code on the side | Yes | Optional | [vscode.md](vscode.md) |
| **Google Colab** | Zero local install, quick experiments | Partial | Optional | [colab.md](colab.md) |
| **Local MkDocs only** | Previewing / editing the course site | Yes | N/A | See below |
| **Live GCP (Terraform)** | Real Cloud SQL, Vertex AI, GCS for the optional live lab paths | No | Yes | [gcp-setup.md](gcp-setup.md) |

---

## Environment details

=== "Docker + JupyterLab"

    **Primary recommended path for the labs.**

    ```bash
    # from repository root
    docker compose up --build
    # → http://localhost:8888
    ```

    or

    ```bash
    make jupyter
    ```

    - Consistent Python 3.11 stack  
    - All lab notebooks and source mounted live  
    - Works fully offline; mount Application Default Credentials when you want live GCP  

    Full instructions → [Docker / JupyterLab Environment](docker.md)

=== "VS Code (Dev Containers)"

    Open the repository root in VS Code and choose **“Reopen in Container”**.  
    Uses the same Docker image as the Jupyter stack so the environment stays identical.

    Full instructions → [VS Code + Container Workflow](vscode.md)

=== "VS Code (attach to running Compose)"

    1. Start the stack: `docker compose up --build`  
    2. In VS Code: Command Palette → **Dev Containers: Attach to Running Container**  
    3. Select the course container  

    Useful when you already have JupyterLab open and also want the IDE.

    Full instructions → [VS Code + Container Workflow](vscode.md)

=== "Google Colab"

    Upload or open the lab notebooks in Colab.  
    Good for quick experiments when you cannot install Docker.

    Full instructions → [Google Colab](colab.md)

=== "Local documentation only"

    Preview the MkDocs site without running any labs:

    ```bash
    make docs-serve
    # or
    pip install -r requirements-docs.txt
    mkdocs serve
    ```

    Open http://127.0.0.1:8000

=== "Live GCP (Terraform)"

    Provisions a cost-controlled set of Google Cloud resources (Cloud SQL + pgvector, GCS, service account, etc.) designed to stay under **$50 / month**.

    ```bash
    cd terraform
    cp environments/student.tfvars environments/my.tfvars
    # set your project_id
    terraform init
    terraform apply -var-file=environments/my.tfvars
    ```

    Vertex AI Vector Search and AlloyDB are **disabled by default** to protect the budget.

    Full instructions → [GCP Setup](gcp-setup.md) and [terraform/README.md](../../terraform/README.md)

---

## Choosing an environment

| Goal | Suggested environment |
|------|-----------------------|
| Complete the labs offline | Docker + JupyterLab |
| Debug / develop with a full IDE | VS Code Dev Containers |
| Quick experiment, no local Docker | Google Colab |
| Test against real Cloud SQL / Vertex AI | Docker (or VS Code) **+** Terraform GCP stack |
| Edit or preview course documentation only | Local MkDocs |

---

## Adding a new environment

When a new runtime option is introduced:

1. Create a detailed guide under `docs/resources/` (e.g. `resources/new-env.md`).
2. Add a row to the table at the top of this page.
3. Add a new tab (or section) under “Environment details”.
4. Update the navigation in `mkdocs.yml` if the new guide should appear in the sidebar.
