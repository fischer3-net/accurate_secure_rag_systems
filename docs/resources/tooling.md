# Recommended Tooling & Stack

| Layer | Technology / GCP Product |
| :--- | :--- |
| **Language & Runtime** | Python 3.11+, Asyncio |
| **LLM & Embeddings** | Vertex AI Gemini 1.5 Pro / Flash, `text-embedding-004` (or current equivalent) |
| **Vector & Hybrid Storage** | Vertex AI Vector Search, AlloyDB (`pgvector`), BigQuery |
| **Graph Storage (Optional)** | Neo4j on GCP / Cloud Spanner Graph |
| **Frameworks** | LangChain / LlamaIndex / Vertex AI SDK, Pydantic |
| **Evaluation Frameworks** | Ragas, Vertex AI Evaluation SDK, `pytest` |
| **CI/CD & DevOps** | GCP Cloud Build, Artifact Registry, Secret Manager, GitHub Actions |

## Local / Cloud Development Tips

- Prefer Vertex AI Workbench or Colab Enterprise for notebooks that need direct GCP authentication.
- Use Application Default Credentials (ADC) everywhere possible.
- Keep secrets in Secret Manager; never hard-code keys.

## Student Jupyter Environment

For a zero-install notebook experience, use the course Docker image:

```bash
docker compose up --build
```

Details: [Docker / JupyterLab Environment](docker.md).
