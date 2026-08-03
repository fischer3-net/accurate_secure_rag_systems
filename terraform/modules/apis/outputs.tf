output "enabled_services" {
  description = "List of APIs that were requested."
  value = concat(
    [for s in google_project_service.required : s.service],
    var.enable_alloydb ? ["alloydb.googleapis.com"] : [],
  )
}
