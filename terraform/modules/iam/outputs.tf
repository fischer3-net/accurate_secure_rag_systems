output "service_account_email" {
  description = "Email of the workshop service account."
  value       = google_service_account.workshop.email
}

output "service_account_name" {
  description = "Fully-qualified name of the workshop service account."
  value       = google_service_account.workshop.name
}

output "service_account_id" {
  description = "Unique ID of the workshop service account."
  value       = google_service_account.workshop.unique_id
}
