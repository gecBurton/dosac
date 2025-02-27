
resource "scaleway_rdb_instance" main {
   region         = var.region
   name           = "${var.project_name}-instance"
   node_type      = "DB-DEV-S"
   engine         = "PostgreSQL-14"
   is_ha_cluster  = false
   disable_backup = true
   user_name      = "root"
   password       = var.postgres_password
}

resource "scaleway_rdb_database" "main" {
  instance_id    = scaleway_rdb_instance.main.id
  name           = "${var.project_name}-database"
  region         = var.region
}

resource "scaleway_rdb_user" "main" {
  instance_id = scaleway_rdb_instance.main.id
  name        = var.postgres_user
  password    = var.postgres_password
  is_admin    = true
}

resource "scaleway_rdb_privilege" "main" {
  instance_id   = scaleway_rdb_instance.main.id
  user_name     = scaleway_rdb_user.main.name
  database_name = scaleway_rdb_database.main.name
  permission    = "all"
}

resource "scaleway_object_bucket" "bucket" {
  name = "${var.project_name}-static"
  region = var.region
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

