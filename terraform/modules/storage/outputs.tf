output "bucket_name" {
  description = "Name of the workshop Cloud Storage bucket."
  value       = google_storage_bucket.workshop.name
}

output "bucket_url" {
  description = "gs:// URL of the workshop bucket."
  value       = "gs://${google_storage_bucket.workshop.name}"
}
