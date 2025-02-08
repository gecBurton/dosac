terraform {
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "2.41.2"
    }
  }
}

provider "scaleway" {
  access_key      = var.access_key
  secret_key      = var.secret_key
  organization_id = var.organization_id
  project_id      = var.project_id
}
