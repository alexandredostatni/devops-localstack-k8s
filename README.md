# Local DevOps Project: Python API with Simulated AWS, Kubernetes, and Monitoring

## Overview
This project deploys a simple Python FastAPI application that stores and retrieves data using simulated AWS S3 and DynamoDB via LocalStack. The app is containerized with Docker, orchestrated on a local Kubernetes cluster (using Kind), provisioned with Terraform, configured with Ansible, monitored with Prometheus and Grafana, and automated via GitHub Actions CI/CD.

Key Features:
- **Simulated AWS**: LocalStack for S3 (file storage) and DynamoDB (key-value store).
- **Application**: FastAPI REST API with endpoints `/upload` (save to S3/DynamoDB) and `/retrieve` (get from S3/DynamoDB). Exposes Prometheus metrics at `/metrics`.
- **IaC**: Terraform provisions LocalStack resources.
- **Containerization**: Docker builds the app image.
- **Orchestration**: Kubernetes (Kind) deploys the app, Prometheus, and Grafana.
- **Configuration**: Ansible sets up Kubernetes add-ons like Node Exporter for metrics.
- **Monitoring**: Prometheus scrapes app/cluster metrics; Grafana dashboards visualize them.
- **CI/CD**: GitHub Actions workflow for build, test, deploy, and verify.

## Learning Objectives
- Understand IaC with Terraform and local AWS simulation.
- Build and deploy containerized apps on Kubernetes.
- Automate configurations with Ansible.
- Implement observability with Prometheus/Grafana.
- Set up CI/CD pipelines with GitHub Actions.
- Practice idempotency, security (e.g., no hard-coded secrets), and troubleshooting.

## Prerequisites
- Linux OS (e.g., Ubuntu 22.04+).
- Docker (v20+).
- Kind (v0.20+) or Minikube for local Kubernetes.
- Terraform (v1.5+).
- Ansible (v2.14+).
- Python 3.10+ with pip.
- Git and GitHub account (for Actions).
- kubectl (v1.27+ matching Kind).
- LocalStack CLI (install via `pip install localstack`).
- Helm (v3+) for optional chart deployments (not required here).

Install prerequisites:
```bash
sudo apt update && sudo apt install -y docker.io python3-pip git curl
pip install localstack ansible
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install kubectl /usr/local/bin/
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 && chmod 700 get_helm.sh && ./get_helm.sh
wget https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip && unzip terraform_1.5.7_linux_amd64.zip && sudo mv terraform /usr/local/bin/

project-root/
├── README.md
├── app/
│   ├── main.py          # FastAPI app code
│   ├── requirements.txt # Python dependencies
│   └── Dockerfile       # Docker build for app
├── infra/
│   └── terraform/
│       ├── main.tf      # Terraform config for LocalStack
│       ├── variables.tf
│       └── outputs.tf
├── k8s/
│   ├── deployment.yaml  # Kubernetes Deployment for app
│   ├── service.yaml     # Service for app
│   ├── prometheus/      # Prometheus manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── configmap.yaml  # prometheus.yml
│   └── grafana/         # Grafana manifests
│       ├── deployment.yaml
│       ├── service.yaml
│       └── configmap.yaml  # Dashboards config
├── ansible/
│   ├── playbook.yml     # Ansible playbook for K8s setup
│   └── inventory.ini    # Local inventory
├── monitoring/
│   └── dashboards/      # JSON files for Grafana dashboards (e.g., app-metrics.json)
├── .github/
│   └── workflows/
│       └── ci-cd.yml    # GitHub Actions workflow
└── tests/               # Optional: Unit tests for app (e.g., test_main.py)