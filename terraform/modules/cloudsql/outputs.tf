output "instance_name" {
  description = "Cloud SQL instance name."
  value       = google_sql_database_instance.workshop.name
}

output "connection_name" {
  description = "Connection name used by the Cloud SQL Auth Proxy (project:region:instance)."
  value       = google_sql_database_instance.workshop.connection_name
}

output "public_ip" {
  description = "Public IP address of the instance."
  value       = google_sql_database_instance.workshop.public_ip_address
}

output "database_name" {
  value = google_sql_database.app.name
}

output "db_user" {
  value = google_sql_user.app.name
}

output "db_password_secret_id" {
  description = "Secret Manager secret ID that holds the database password."
  value       = google_secret_manager_secret.db_password.secret_id
}

output "db_password" {
  description = "Database password (sensitive)."
  value       = random_password.db_password.result
  sensitive   = true
}
