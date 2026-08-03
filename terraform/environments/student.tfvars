# -----------------------------------------------------------------------------
# Student workshop defaults – designed to stay under $50 / month
# -----------------------------------------------------------------------------

# REQUIRED – replace with your own project
project_id = "YOUR_GCP_PROJECT_ID"

region      = "us-central1"
name_prefix = "rag-workshop"

# Feature flags
enable_cloud_sql     = true   # ~$10–25/mo for db-f1-micro
enable_vector_search = false  # KEEP FALSE – can exceed $100–300/mo alone
enable_alloydb       = false  # KEEP FALSE – far above budget

# Cloud SQL sizing (do not increase if you want to stay under $50)
cloudsql_tier              = "db-f1-micro"
cloudsql_disk_size_gb      = 20
cloudsql_availability_type = "ZONAL"
cloudsql_database_name     = "rag_workshop"
cloudsql_user              = "rag_user"

labels = {
  project     = "accurate-secure-rag-systems"
  environment = "student-workshop"
  managed-by  = "terraform"
  cost-center = "workshop"
}
