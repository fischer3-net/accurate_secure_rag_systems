# GCP Workshop Infrastructure (Terraform)

This package provisions the minimum Google Cloud resources needed to run the live portions of the **Advanced RAG Architecture, Custom Skills & Evaluation on Google Cloud Platform** course.

**Design goal:** stay comfortably under **$50 USD / month** for a typical student project when using the default configuration.

## What gets created (default)

| Resource | Purpose | Approx. monthly cost |
|----------|---------|----------------------|
| Service Account + IAM | Least-privilege identity for labs & Docker | free |
| Cloud Storage bucket | Documents, evaluation artifacts, index files | < $1 |
| Cloud SQL PostgreSQL 15 (`db-f1-micro`, 20 GB SSD, zonal) | “AlloyDB-style” hybrid SQL + pgvector store | ~$10–25 |
| Secret Manager secret | Stores the database password | free tier |
| Required APIs | Vertex AI, Cloud SQL, Storage, etc. | free |

**Explicitly disabled by default (do not enable unless you accept higher cost):**

- Vertex AI Vector Search (Matching Engine) – can easily exceed $100–300/mo
- AlloyDB – far above the $50 budget

Vertex AI **API usage** (Gemini, embeddings, function calling) is pay-per-use and depends on how many requests you make. For normal lab volume it usually stays well under $10–15.

## Prerequisites

1. A GCP project you own (or a sandbox with billing enabled).
2. `gcloud` CLI authenticated with sufficient permissions (`roles/owner` or equivalent on the project is simplest for a personal workshop project).
3. Terraform ≥ 1.5.

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

## Quick start

```bash
cd terraform

# 1. Edit the student variables
cp environments/student.tfvars environments/my.tfvars
# → set project_id = "your-real-project-id"

# 2. Initialize
terraform init

# 3. Review the plan
terraform plan -var-file=environments/my.tfvars

# 4. Apply
terraform apply -var-file=environments/my.tfvars
```

After a successful apply you will see an `env_snippet` output. Copy it into your shell or into the Docker environment:

```bash
# Example
eval "$(terraform output -raw env_snippet)"
```

You can also fetch the database password when needed:

```bash
gcloud secrets versions access latest --secret="$(terraform output -raw cloudsql_password_secret_id)"
```

**First-time Cloud SQL setup (pgvector):** after the instance is ready, connect once and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

## Using with the course Docker environment

The workshop Docker Compose setup already supports mounting Application Default Credentials. After `terraform apply`:

```bash
# From the repository root
export GOOGLE_APPLICATION_CREDENTIALS=...   # or rely on gcloud ADC
docker compose up --build
```

The environment variables printed by `terraform output env_snippet` can be placed in a `.env` file that `docker-compose.yml` reads.

## Cost control rules (important)

1. **Never set `enable_vector_search = true`** unless you have explicitly accepted the higher cost and understand how to destroy the index endpoint.
2. **Never set `enable_alloydb = true`** for a student project.
3. Do not change `cloudsql_tier` to anything larger than `db-f1-micro` or `db-g1-small` if you want to stay near the $50 ceiling.
4. Destroy the stack when you are finished for the day/week:

   ```bash
   terraform destroy -var-file=environments/my.tfvars
   ```

5. Monitor spend in the GCP Console → Billing → Reports. Set a budget alert at $40 as a safety net.

## Destroy / clean-up

```bash
terraform destroy -var-file=environments/my.tfvars
```

Because `force_destroy = true` is set on the bucket and `deletion_protection = false` is set on Cloud SQL, a normal destroy should remove everything. If you previously enabled Vector Search, confirm that the index endpoint and deployed index are gone in the Vertex AI console.

## Optional: enable Vertex AI Vector Search

Only do this if you need a live Matching Engine backend and have budget headroom:

```hcl
enable_vector_search = true
```

Then re-apply. Expect significantly higher cost and longer apply times (index building). Prefer the offline / in-memory Vector Search style implementations that ship with the labs for most of the course.

## Module layout

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── versions.tf
├── providers.tf
├── environments/
│   └── student.tfvars
└── modules/
    ├── apis/
    ├── iam/
    ├── storage/
    ├── cloudsql/
    └── vertex_vector_search/   # only when flag is true
```

## Alignment with course labs

| Week / Lab | How this infrastructure is used |
|------------|---------------------------------|
| Week 1 – Hybrid retrieval | Vertex AI embeddings (API) + optional GCS |
| Week 2 – Storage | Cloud SQL + pgvector = live “AlloyDB-style” backend; Vector Search module = live pure-semantic backend |
| Week 3 – Skills / Function calling | Vertex AI (Gemini + tool declarations) via the workshop SA |
| Week 4 – Evaluation | GCS for artifacts, Vertex AI for model-based metrics |
| Capstone | All of the above |

The labs remain offline-first; this package simply makes the optional live paths easy and safe to turn on.
