import os
import argparse


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate Kubernetes, Helm, and ArgoCD files for a repository."
    )
    parser.add_argument(
        "repository_name", help="The name of the repository (e.g. stock-tech-movavg)"
    )
    parser.add_argument(
        "--environment",
        choices=["dev", "prod"],
        default="dev",
        help="Specify the environment (dev or prod)",
    )
    return parser.parse_args()


def create_directories() -> None:
    """Ensure necessary directories exist."""
    os.makedirs("k8s", exist_ok=True)
    os.makedirs("helm/templates", exist_ok=True)
    os.makedirs(".github/workflows", exist_ok=True)


def get_env_values(repository_name: str, environment: str) -> dict[str, str | int]:
    """Define environment-specific values."""
    return {
        "replica_count": 1 if environment == "dev" else 3,
        "log_level": "DEBUG" if environment == "dev" else "INFO",
        "rabbitmq_host": f"{repository_name}-rabbitmq.{environment}.internal",
        "rabbitmq_queue": f"{repository_name}_{environment}_queue",
    }


def generate_files(
    repository_name: str, environment: str, env_values: dict[str, str | int]
) -> dict[str, str]:
    """Generate Kubernetes and Helm configuration files."""
    files = {
        "k8s/deployment.yaml": f"""\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {repository_name}
spec:
  replicas: {env_values["replica_count"]}
  selector:
    matchLabels:
      app: {repository_name}
  template:
    metadata:
      labels:
        app: {repository_name}
    spec:
      containers:
        - name: {repository_name}
          image: your-registry/{repository_name}:latest
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: "{environment}"
            - name: LOG_LEVEL
              value: "{env_values["log_level"]}"
            - name: RABBITMQ_HOST
              value: "{env_values["rabbitmq_host"]}"
            - name: RABBITMQ_QUEUE
              value: "{env_values["rabbitmq_queue"]}"
""",
        "k8s/service.yaml": f"""\
apiVersion: v1
kind: Service
metadata:
  name: {repository_name}-service
spec:
  selector:
    app: {repository_name}
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
""",
        "helm/values.yaml": f"""\
replicaCount: {env_values["replica_count"]}

image:
  repository: your-registry/{repository_name}
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  port: 80
  targetPort: 8000

environment:
  ENVIRONMENT: "{environment}"
  LOG_LEVEL: "{env_values["log_level"]}"
  RABBITMQ_HOST: "{env_values["rabbitmq_host"]}"
  RABBITMQ_QUEUE: "{env_values["rabbitmq_queue"]}"
""",
    }
    return files


def write_files(files: dict[str, str]) -> None:
    """Write generated files to disk."""
    for filename, content in files.items():
        with open(filename, "w") as f:
            f.write(content)


def main() -> None:
    """Main function to run the script."""
    args = parse_arguments()
    create_directories()
    env_values = get_env_values(args.repository_name, args.environment)
    files = generate_files(args.repository_name, args.environment, env_values)
    write_files(files)

    print(
        f"✅ Kubernetes, Helm, and ArgoCD files generated for {args.repository_name} (Environment: {args.environment})"
    )


if __name__ == "__main__":
    main()
