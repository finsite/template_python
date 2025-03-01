import os
import subprocess
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Generate Kubernetes, Helm, and ArgoCD files for a repository.")
parser.add_argument("repo_name", help="The name of the repository")
parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="Specify the environment (dev or prod)")
args = parser.parse_args()

repo_name = args.repo_name
env = args.env

# Ensure necessary directories exist
os.makedirs("k8s", exist_ok=True)
os.makedirs("helm/templates", exist_ok=True)
os.makedirs(".github/workflows", exist_ok=True)

# Define environment-specific values
replica_count = 1 if env == "dev" else 3
log_level = "debug" if env == "dev" else "info"
rabbitmq_host = f"{repo_name}-rabbitmq.dev.internal" if env == "dev" else f"{repo_name}-rabbitmq.prod.internal"
rabbitmq_queue = f"{repo_name}_dev_queue" if env == "dev" else f"{repo_name}_prod_queue"

# Define file contents
files = {
    "k8s/deployment.yaml": f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {repo_name}
spec:
  replicas: {replica_count}
  selector:
    matchLabels:
      app: {repo_name}
  template:
    metadata:
      labels:
        app: {repo_name}
    spec:
      containers:
        - name: {repo_name}
          image: your-registry/{repo_name}:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "{env}"
            - name: LOG_LEVEL
              value: "{log_level}"
            - name: RABBITMQ_HOST
              value: "{rabbitmq_host}"
            - name: RABBITMQ_QUEUE
              value: "{rabbitmq_queue}"
""",
    "k8s/service.yaml": f"""\
apiVersion: v1
kind: Service
metadata:
  name: {repo_name}-service
spec:
  selector:
    app: {repo_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
""",
    "helm/values.yaml": f"""\
replicaCount: {replica_count}

image:
  repository: your-registry/{repo_name}
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

environment:
  ENVIRONMENT: "{env}"
  LOG_LEVEL: "{log_level}"
  RABBITMQ_HOST: "{rabbitmq_host}"
  RABBITMQ_QUEUE: "{rabbitmq_queue}"
""",
    "README.md": f"""\
# {repo_name}

## 🚀 Deployment Options

This repository supports multiple deployment methods:

### 🛠 1. Kubernetes (Manual)
Manually apply Kubernetes manifests in the `k8s/` folder:

```sh
kubectl apply -f k8s/