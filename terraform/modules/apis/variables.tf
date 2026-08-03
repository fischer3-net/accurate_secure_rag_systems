variable "project_id" {
  type = string
}

variable "enable_vector_search" {
  type    = bool
  default = false
}

variable "enable_alloydb" {
  type    = bool
  default = false
}
