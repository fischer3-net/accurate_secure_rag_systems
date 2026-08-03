output "index_id" {
  value = google_vertex_ai_index.workshop.id
}

output "index_endpoint_id" {
  value = google_vertex_ai_index_endpoint.workshop.id
}

output "deployed_index_id" {
  value = google_vertex_ai_index_endpoint_deployed_index.workshop.deployed_index_id
}
