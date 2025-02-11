resource "null_resource" "kubeconfig" {
  depends_on = [scaleway_k8s_pool.pool]
  triggers = {
    host                   = scaleway_k8s_cluster.k8s-cluster.kubeconfig[0].host
    token                  = scaleway_k8s_cluster.k8s-cluster.kubeconfig[0].token
    cluster_ca_certificate = scaleway_k8s_cluster.k8s-cluster.kubeconfig[0].cluster_ca_certificate
  }
}

provider "kubernetes" {
  host  = null_resource.kubeconfig.triggers.host
  token = null_resource.kubeconfig.triggers.token
  cluster_ca_certificate = base64decode(
    null_resource.kubeconfig.triggers.cluster_ca_certificate
  )
}
provider "helm" {
  kubernetes {
  host  = null_resource.kubeconfig.triggers.host
  token = null_resource.kubeconfig.triggers.token
  cluster_ca_certificate = base64decode(
    null_resource.kubeconfig.triggers.cluster_ca_certificate
  )
  }
}

resource "kubernetes_secret" "app_secret" {
  metadata {
    name = "${var.project_name}-secret"
  }

  data = {
    LLM_MODEL               = "gpt-4o-mini",
    LLM_MODEL_PROVIDER      = "openai",
    EMBEDDING_MODEL         = "text-embedding-3-large",
    OPENAI_API_VERSION      = "2024-02-01",
    AWS_STORAGE_BUCKET_NAME = scaleway_object_bucket.bucket.name,
    AWS_S3_ENDPOINT_URL     = scaleway_object_bucket.bucket.api_endpoint,
    APP_HOST                = "51.159.112.167", # =web_service_external_ip, chicken and egg - deploy with anything and then change it
    DEBUG                   = true,
    SECRET_KEY              = "Postgres123!",
    POSTGRES_HOST           = scaleway_rdb_instance.main.endpoint_ip,
    POSTGRES_PORT           = scaleway_rdb_instance.main.endpoint_port,
    POSTGRES_NAME           = scaleway_rdb_database.main.name,
    POSTGRES_USER           = var.postgres_user,
    POSTGRES_PASSWORD       = scaleway_rdb_instance.main.password,
    AWS_ACCESS_KEY_ID       = var.access_key,
    AWS_SECRET_ACCESS_KEY   = var.secret_key,
    OPENAI_API_KEY          = var.openai_api_key
  }
}

resource "kubernetes_deployment_v1" "web" {

  metadata {
    name = "${var.project_name}-web"
  }

  spec {
    replicas = 3
    selector {
      match_labels = {
        app = "${var.project_name}-web"
      }
    }
    template {
      metadata { labels = { "app" : "${var.project_name}-web" } }
      spec {
        container {
          name  = "${var.project_name}-web"
          image = "rg.fr-par.scw.cloud/account-registry/dosac-web:latest"
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secret.metadata[0].name
            }
          }
          port {
            container_port = 8080
          }
        }
      }
    }
  }
}


resource "kubernetes_deployment_v1" "worker" {

  metadata {
    name = "${var.project_name}-worker"
  }

  spec {
    replicas = 1
    selector {
      match_labels = {
        app = "${var.project_name}-worker"
      }
    }
    template {
      metadata { labels = { "app" : "${var.project_name}-worker" } }
      spec {
        container {
          name  = "${var.project_name}-worker"
          image = "rg.fr-par.scw.cloud/account-registry/dosac-web:latest"
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secret.metadata[0].name
            }
          }
          command = ["poetry", "run", "python", "manage.py", "qcluster"]
        }
      }
    }
  }
}

resource "kubernetes_service" "ingres" {
  metadata {
    name = "ingres"
  }
  spec {
    type = "LoadBalancer"

    selector = {
      app = "${var.project_name}-web"
    }

    port {
      protocol    = "TCP"
      port        = 80
      target_port = "8080"
    }
  }
}

output "web_service_external_ip" {
  value = kubernetes_service.ingres.status[0].load_balancer[0].ingress[0].ip
}