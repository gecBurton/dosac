variable "access_key" {
  type = string
  sensitive = true
}

variable "secret_key" {
  type = string
  sensitive = true
}

variable "organization_id" {
  type = string
  sensitive = true
}

variable "project_id" {
  type = string
  sensitive = true
}

variable "region" {
  type = string
  default = "region"
}

variable "postgres_name" {
  type = string
  default = "postgres"
}

variable "postgres_password" {
  type = string
  sensitive = true
}

variable "postgres_user" {
  type = string
  default = "postgres"
}

variable "postgres_host" {
  type = string
  default = "postgres"
}

variable "postgres_port" {
  type = string
  default = "5432"
}

