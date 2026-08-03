# -----------------------------------------------------------------------------
# Primary outputs consumed by Docker / notebooks / lab code
# -----------------------------------------------------------------------------

output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "service_account_email" {
  description = "Use this SA with Application Default Credentials."
  value       = module.iam.service_account_email
}

output "gcs_bucket" {
  value = module.storage.bucket_name
}

output "gcs_bucket_url" {
  value = module.storage.bucket_url
}

# Cloud SQL (present only when enable_cloud_sql = true)
output "cloudsql_connection_name" {
  value       = try(module.cloudsql[0].connection_name, null)
  description = "project:region:instance – used by Cloud SQL Auth Proxy"
}

output "cloudsql_public_ip" {
  value = try(module.cloudsql[0].public_ip, null)
}

output "cloudsql_database" {
  value = try(module.cloudsql[0].database_name, null)
}

output "cloudsql_user" {
  value = try(module.cloudsql[0].db_user, null)
}

output "cloudsql_password_secret_id" {
  value       = try(module.cloudsql[0].db_password_secret_id, null)
  description = "Fetch the password with: gcloud secrets versions access latest --secret=<id>"
}

output "cloudsql_password" {
  value     = try(module.cloudsql[0].db_password, null)
  sensitive = true
}

# Vector Search (present only when enable_vector_search = true)
output "vector_search_index_id" {
  value = try(module.vector_search[0].index_id, null)
}

output "vector_search_endpoint_id" {
  value = try(module.vector_search[0].index_endpoint_id, null)
}

# Convenience block that can be copied into .env or docker-compose
output "env_snippet" {
  description = "Ready-to-paste environment variables for the workshop Docker environment."
  value = <<-EOT
    export GOOGLE_CLOUD_PROJECT="${var.project_id}"
    export GOOGLE_CLOUD_REGION="${var.region}"
    export RAG_GCS_BUCKET="${module.storage.bucket_name}"
    export RAG_SERVICE_ACCOUNT="${module.iam.service_account_email}"
    %{if var.enable_cloud_sql~}
    export RAG_CLOUDSQL_CONNECTION="${module.cloudsql[0].connection_name}"
    export RAG_CLOUDSQL_HOST="${module.cloudsql[0].public_ip}"
    export RAG_CLOUDSQL_DB="${module.cloudsql[0].database_name}"
    export RAG_CLOUDSQL_USER="${module.cloudsql[0].db_user}"
    export RAG_CLOUDSQL_PASSWORD_SECRET="${module.cloudsql[0].db_password_secret_id}"
    %{endif~}
  EOT
}
