# -----------------------------------------------------------------------------
# Core
# -----------------------------------------------------------------------------
variable "project_id" {
  description = "GCP project ID where resources will be created."
  type        = string
}

variable "region" {
  description = "Primary region for regional resources (Cloud SQL, GCS, Vertex)."
  type        = string
  default     = "us-central1"
}

variable "name_prefix" {
  description = "Prefix applied to most resource names (keeps them unique and identifiable)."
  type        = string
  default     = "rag-workshop"
}

# -----------------------------------------------------------------------------
# Feature flags (cost control)
# -----------------------------------------------------------------------------
variable "enable_cloud_sql" {
  description = "Provision a small Cloud SQL PostgreSQL instance with pgvector. Recommended for the AlloyDB-style labs."
  type        = bool
  default     = true
}

variable "enable_vector_search" {
  description = "Provision a Vertex AI Vector Search index. DISABLED by default – this is the most expensive component."
  type        = bool
  default     = false
}

variable "enable_alloydb" {
  description = "Provision AlloyDB. Keep false for students – cost exceeds the $50 monthly budget."
  type        = bool
  default     = false
}

# -----------------------------------------------------------------------------
# Cloud SQL sizing (kept deliberately small to stay under $50/mo)
# -----------------------------------------------------------------------------
variable "cloudsql_tier" {
  description = "Cloud SQL machine tier. db-f1-micro is the cheapest shared-core option."
  type        = string
  default     = "db-f1-micro"
}

variable "cloudsql_disk_size_gb" {
  description = "SSD disk size in GB for Cloud SQL."
  type        = number
  default     = 20
}

variable "cloudsql_availability_type" {
  description = "ZONAL is required to stay within budget. Do not set REGIONAL."
  type        = string
  default     = "ZONAL"
}

variable "cloudsql_database_name" {
  description = "Name of the application database created inside Cloud SQL."
  type        = string
  default     = "rag_workshop"
}

variable "cloudsql_user" {
  description = "Database user name."
  type        = string
  default     = "rag_user"
}

# -----------------------------------------------------------------------------
# Vertex AI Vector Search (only used when enable_vector_search = true)
# -----------------------------------------------------------------------------
variable "vector_search_dimensions" {
  description = "Embedding dimensions (768 for text-embedding-004 / gecko, 768 or 3072 for others)."
  type        = number
  default     = 768
}

variable "vector_search_approx_neighbors" {
  description = "Default number of neighbors returned by the index."
  type        = number
  default     = 10
}

# -----------------------------------------------------------------------------
# Labels / tagging
# -----------------------------------------------------------------------------
variable "labels" {
  description = "Labels applied to all supported resources."
  type        = map(string)
  default = {
    project     = "accurate-secure-rag-systems"
    environment = "student-workshop"
    managed-by  = "terraform"
  }
}
