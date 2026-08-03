# Small, single-zone Cloud SQL PostgreSQL instance intended for the
# "AlloyDB-style" hybrid (SQL + pgvector) labs. Sized to stay well under
# the $50 monthly workshop budget.

resource "random_password" "db_password" {
  length           = 24
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "google_sql_database_instance" "workshop" {
  name             = "${var.name_prefix}-pg"
  project          = var.project_id
  region           = var.region
  database_version = "POSTGRES_15"

  settings {
    tier              = var.tier
    availability_type = var.availability_type
    disk_size         = var.disk_size_gb
    disk_type         = "PD_SSD"
    disk_autoresize   = false

    ip_configuration {
      ipv4_enabled = true # public IP for simplicity in a workshop setting
      # Students should still use strong passwords and prefer Cloud SQL Auth Proxy
      # or authorized networks in real deployments.
      authorized_networks {
        name  = "allow-all-workshop"
        value = "0.0.0.0/0"
      }
    }

    # pgvector is enabled after first connection with:
    #   CREATE EXTENSION IF NOT EXISTS vector;
    # No special database flag is required on current Cloud SQL PostgreSQL 15 images.

    backup_configuration {
      enabled                        = false # disable to save cost
      point_in_time_recovery_enabled = false
    }

    maintenance_window {
      day  = 7 # Sunday
      hour = 3
    }

    user_labels = var.labels
  }

  deletion_protection = false # students must be able to destroy easily

  depends_on = [var.apis_dependency]
}

resource "google_sql_database" "app" {
  name     = var.database_name
  instance = google_sql_database_instance.workshop.name
  project  = var.project_id
}

resource "google_sql_user" "app" {
  name     = var.db_user
  instance = google_sql_database_instance.workshop.name
  project  = var.project_id
  password = random_password.db_password.result
}

# Store the password in Secret Manager so notebooks / Docker can fetch it
# without hard-coding secrets.
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.name_prefix}-db-password"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret_iam_member" "workshop_sa_accessor" {
  secret_id = google_secret_manager_secret.db_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}
