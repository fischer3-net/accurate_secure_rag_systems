# Enable the minimum set of APIs required by the workshop.
# Optional / expensive APIs are gated by the feature flags passed from the root module.

resource "google_project_service" "required" {
  for_each = toset([
    "aiplatform.googleapis.com",          # Vertex AI (Gemini, embeddings, function calling)
    "sqladmin.googleapis.com",            # Cloud SQL Admin
    "secretmanager.googleapis.com",       # Secret Manager
    "storage.googleapis.com",             # Cloud Storage
    "iam.googleapis.com",                 # IAM
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "compute.googleapis.com",             # needed for Cloud SQL networking
  ])

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_project_service" "optional_vector_search" {
  count = var.enable_vector_search ? 1 : 0

  project            = var.project_id
  service            = "aiplatform.googleapis.com" # already covered, kept for clarity
  disable_on_destroy = false
}

resource "google_project_service" "optional_alloydb" {
  count = var.enable_alloydb ? 1 : 0

  project            = var.project_id
  service            = "alloydb.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "optional_cloudbuild" {
  project            = var.project_id
  service            = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "optional_bigquery" {
  project            = var.project_id
  service            = "bigquery.googleapis.com"
  disable_on_destroy = false
}
