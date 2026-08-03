# -----------------------------------------------------------------------------
# Accurate Secure RAG Systems – Student GCP Workshop Infrastructure
# Target monthly cost (default configuration): well under $50
# -----------------------------------------------------------------------------

module "apis" {
  source = "./modules/apis"

  project_id           = var.project_id
  enable_vector_search = var.enable_vector_search
  enable_alloydb       = var.enable_alloydb
}

module "iam" {
  source = "./modules/iam"

  project_id  = var.project_id
  name_prefix = var.name_prefix

  depends_on = [module.apis]
}

module "storage" {
  source = "./modules/storage"

  project_id            = var.project_id
  region                = var.region
  name_prefix           = var.name_prefix
  service_account_email = module.iam.service_account_email
  labels                = var.labels

  depends_on = [module.apis]
}

module "cloudsql" {
  source = "./modules/cloudsql"
  count  = var.enable_cloud_sql ? 1 : 0

  project_id            = var.project_id
  region                = var.region
  name_prefix           = var.name_prefix
  tier                  = var.cloudsql_tier
  disk_size_gb          = var.cloudsql_disk_size_gb
  availability_type     = var.cloudsql_availability_type
  database_name         = var.cloudsql_database_name
  db_user               = var.cloudsql_user
  service_account_email = module.iam.service_account_email
  labels                = var.labels
  apis_dependency       = module.apis

  depends_on = [module.apis, module.iam]
}

module "vector_search" {
  source = "./modules/vertex_vector_search"
  count  = var.enable_vector_search ? 1 : 0

  project_id      = var.project_id
  region          = var.region
  name_prefix     = var.name_prefix
  bucket_name     = module.storage.bucket_name
  dimensions      = var.vector_search_dimensions
  approx_neighbors = var.vector_search_approx_neighbors
  labels          = var.labels

  depends_on = [module.apis, module.storage]
}
