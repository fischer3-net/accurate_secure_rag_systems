variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "name_prefix" {
  type = string
}

variable "service_account_email" {
  type = string
}

variable "labels" {
  type    = map(string)
  default = {}
}
