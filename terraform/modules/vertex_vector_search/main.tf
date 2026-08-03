# Optional Vertex AI Vector Search (Matching Engine) resources.
# This module is ONLY instantiated when enable_vector_search = true.
# It is the single largest cost driver and is disabled by default
# to stay under the $50 monthly workshop budget.

resource "google_vertex_ai_index" "workshop" {
  region       = var.region
  display_name = "${var.name_prefix}-index"
  description  = "Workshop Vector Search index (optional – expensive)"

  metadata {
    contents_delta_uri = "gs://${var.bucket_name}/vector-search/initial"
    config {
      dimensions                  = var.dimensions
      approximate_neighbors_count = var.approx_neighbors
      distance_measure_type       = "COSINE_DISTANCE"
      algorithm_config {
        tree_ah_config {
          leaf_node_embedding_count    = 1000
          leaf_nodes_to_search_percent = 10
        }
      }
    }
  }

  index_update_method = "BATCH_UPDATE"

  labels = var.labels
}

resource "google_vertex_ai_index_endpoint" "workshop" {
  region       = var.region
  display_name = "${var.name_prefix}-endpoint"
  description  = "Workshop Vector Search endpoint"

  labels = var.labels
}

# Deploying the index to an endpoint with a dedicated serving node is what
# incurs the majority of the cost. Students should only enable this when
# they explicitly want a live Vector Search backend.
resource "google_vertex_ai_index_endpoint_deployed_index" "workshop" {
  index_endpoint   = google_vertex_ai_index_endpoint.workshop.id
  index            = google_vertex_ai_index.workshop.id
  deployed_index_id = replace("${var.name_prefix}_deployed", "-", "_")

  dedicated_resources {
    machine_spec {
      machine_type = "e2-standard-2"
    }
    min_replica_count = 1
    max_replica_count = 1
  }
}
