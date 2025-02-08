
resource "scaleway_rdb_instance" main {
   region         = var.region
   name           = var.postgres_name
   node_type      = "DB-DEV-S"
   engine         = "PostgreSQL-15"
   is_ha_cluster  = false
   disable_backup = true
   user_name      = var.postgres_user
   password       = var.postgres_password

}

resource "scaleway_rdb_database" "main" {
  instance_id    = scaleway_rdb_instance.main.id
  name           = "${var.project_name}-database"
  region         = var.region
}

resource "scaleway_object_bucket" "bucket" {
  name = "${var.project_name}-bucket"
  region = var.region
}

output "bucket_url" {
  value = "https://${scaleway_object_bucket.bucket.name}.${scaleway_object_bucket.bucket.endpoint}"
}

resource "scaleway_vpc_private_network" "vpc" {
  name = "${var.project_name}-vpc"
  region = var.region
}

resource "scaleway_k8s_cluster" "k8s-cluster" {
  name        = "${var.project_name}-k8s-cluster"
  version     = "1.31.2"
  cni         = "cilium"
  region      = var.region
  delete_additional_resources = false
  private_network_id = scaleway_vpc_private_network.vpc.id
}

resource "scaleway_k8s_pool" "pool" {
  cluster_id  = scaleway_k8s_cluster.k8s-cluster.id
  name        = "${var.project_name}-k8-pool"
  node_type   = "DEV1-M"
  size        = 2
  autoscaling = false
  autohealing = true

  region = var.region
  tags = ["example", "k8s"]
}

output "kubeconfig" {
  value     = scaleway_k8s_cluster.k8s-cluster.kubeconfig[0]
  sensitive = true
  description = "Kubeconfig to access your Kubernetes cluster."
}



