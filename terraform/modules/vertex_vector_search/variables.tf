variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "bucket_name" {
  description = "GCS bucket used for the initial index contents delta."
  type        = string
}

variable "dimensions" {
  type = number
}

variable "approx_neighbors" {
  type = number
}

variable "labels" {
  type    = map(string)
  default = {}
}
