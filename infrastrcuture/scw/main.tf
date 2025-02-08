
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
  name           = "main-database"
}

# resource "scaleway_instance_server" "myapp" {
#    name   = "django-app-server"
#    type   = "DEV1-S"  # Choose an appropriate size
#    image  = "ubuntu-focal"  # Or any other preferred distribution
#  }
#
# resource "scaleway_instance_security_group" "allow_http_postgres" {
#    inbound_rule {
#      action      = "accept"
#      ip_range    = "0.0.0.0/0"
#      protocol    = "tcp"
#      port        = 80    # HTTP
#    }
#    inbound_rule {
#      action      = "accept"
#      ip_range    = "0.0.0.0/0"
#      protocol    = "tcp"
#      port        = 5432  # PostgreSQL
#    }
#  }
#
