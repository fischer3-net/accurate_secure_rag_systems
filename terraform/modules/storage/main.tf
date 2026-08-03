resource "google_storage_bucket" "workshop" {
  name          = "${var.name_prefix}-${var.project_id}-artifacts"
  project       = var.project_id
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  force_destroy               = true # students can destroy without leftover objects

  versioning {
    enabled = false
  }

  labels = var.labels

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Allow the workshop SA full object access on this bucket only
resource "google_storage_bucket_iam_member" "workshop_sa" {
  bucket = google_storage_bucket.workshop.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.service_account_email}"
}
