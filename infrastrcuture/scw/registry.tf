resource "scaleway_registry_namespace" "docker-registry" {
  name   = "account-registry"
  region = var.region
}

output "registry_endpoint" {
  value = scaleway_registry_namespace.docker-registry.endpoint
}
