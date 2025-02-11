
resource "scaleway_rdb_instance" main {
   region         = var.region
   name           = "${var.project_name}-instance"
   node_type      = "DB-DEV-S"
   engine         = "PostgreSQL-14"
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


output "pg_host" {
  value = scaleway_rdb_instance.main.endpoint_ip
}

output "pg_port" {
  value = scaleway_rdb_instance.main.endpoint_port
}

output "pg_password" {
  value = scaleway_rdb_instance.main.password
  sensitive = true
}

output "pg_user" {
  value = scaleway_rdb_instance.main.user_name
}

output "pg_database" {
  value = scaleway_rdb_instance.main.name
}


resource "scaleway_object_bucket" "bucket" {
  name = "${var.project_name}-bucket2"
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

