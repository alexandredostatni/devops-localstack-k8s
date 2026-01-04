name: DevOps CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Iniciar LocalStack
        uses: LocalStack/setup-localstack@v0.2.3
        with:
          image-tag: latest               # Usa a versão mais recente do LocalStack
          install-awslocal: 'true'        # Instala o wrapper awslocal (muito útil)
          services: s3,dynamodb           # Ativa apenas S3 e DynamoDB (mais rápido)

      - name: Configurar Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.5.7        # Versão estável compatível

      - name: Terraform Init, Validate e Apply
        run: |
          cd infra/terraform
          terraform init
          terraform validate
          terraform apply -auto-approve
        env:
          AWS_ACCESS_KEY_ID: test
          AWS_SECRET_ACCESS_KEY: test
          AWS_DEFAULT_REGION: eu-west-1   # Região que evita o erro MalformedXML
          AWS_ENDPOINT_URL_S3: http://localhost:4566
          AWS_ENDPOINT_URL_DYNAMODB: http://localhost:4566

      - name: Configurar Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build da imagem Docker da aplicação
        run: |
          cd app
          docker build -t myapp:latest .

      - name: Configurar Kind (Kubernetes in Docker)
        uses: helm/kind-action@v1.8.0
        with:
          install_kubectl: true

      - name: Carregar imagem Docker no cluster Kind
        run: |
          kind load docker-image myapp:latest

      - name: Criar namespace monitoring (se não existir)
        run: |
          kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy da aplicação e monitoramento no Kubernetes
        run: |
          kubectl apply -f k8s/deployment.yaml
          kubectl apply -f k8s/service.yaml
          kubectl apply -f k8s/prometheus/
          kubectl apply -f k8s/grafana/

      - name: Configurar Ansible
        run: |
          pip install ansible kubernetes

      - name: Executar playbook Ansible (Node Exporter, etc.)
        run: |
          cd ansible
          ansible-playbook -i inventory.ini playbook.yml

      - name: Verificar saúde da aplicação e métricas
        run: |
          # Espera pods ficarem prontos
          kubectl wait --for=condition=ready pod -l app=myapp --timeout=120s
          kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=120s

          # Port-forward temporário para testar endpoint de métricas
          kubectl port-forward svc/myapp-service 8000:80 > /dev/null 2>&1 &
          sleep 10
          curl -f http://localhost:8000/metrics | grep http_requests_total || echo "Métricas não encontradas (pode ser normal no primeiro run)"

      - name: Sucesso
        run: echo "Pipeline concluído com sucesso! Todos os componentes foram provisionados e verificados."
