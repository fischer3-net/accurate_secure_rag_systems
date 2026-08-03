variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "tier" {
  type = string
}

variable "disk_size_gb" {
  type = number
}

variable "availability_type" {
  type = string
}

variable "database_name" {
  type = string
}

variable "db_user" {
  type = string
}

variable "service_account_email" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}

variable "apis_dependency" {
  description = "Used to ensure APIs are enabled before creating the instance."
  type        = any
  default     = null
}
