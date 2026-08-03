# Workshop service account used by Docker / notebooks via Application Default Credentials.

resource "google_service_account" "workshop" {
  account_id   = "${var.name_prefix}-sa"
  display_name = "RAG Workshop Student Service Account"
  description  = "Least-privilege SA for the Accurate Secure RAG Systems workshop labs."
  project      = var.project_id
}

# Predefined roles that cover the majority of lab needs while staying reasonably narrow.
# Students should never use the Owner / Editor roles.

locals {
  workshop_roles = [
    "roles/aiplatform.user",           # Vertex AI (predict, embed, function calling)
    "roles/storage.objectAdmin",       # read/write objects in the workshop bucket
    "roles/secretmanager.secretAccessor",
    "roles/cloudsql.client",           # connect to Cloud SQL
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ]
}

resource "google_project_iam_member" "workshop_roles" {
  for_each = toset(local.workshop_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.workshop.email}"
}

# Optional: allow the SA to act as itself (useful for some Vertex pipelines)
resource "google_service_account_iam_member" "self_user" {
  service_account_id = google_service_account.workshop.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.workshop.email}"
}
