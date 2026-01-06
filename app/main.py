import os
from fastapi import FastAPI
import boto3
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="DevOps LocalStack Demo API")

# Configuração do endpoint do LocalStack via variável de ambiente
# Padrão: http://localhost:4566 → funciona no GitHub Actions (Kind + LocalStack no mesmo runner)
# Localmente, se precisar de host.docker.internal, basta definir: LOCALSTACK_URL=http://host.docker.internal:4566
LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")

# Configuração comum para S3 e DynamoDB
session_config = {
    "endpoint_url": LOCALSTACK_URL,
    "aws_access_key_id": "test",
    "aws_secret_access_key": "test",
    "region_name": "eu-west-1",  # Compatível com a configuração do Terraform
}

# Clientes AWS simulados
s3 = boto3.client("s3", **session_config)
dynamodb = boto3.resource("dynamodb", **session_config)
table = dynamodb.Table("MyDataTable")

# Instrumentação de métricas Prometheus
Instrumentator().instrument(app).expose(app)


@app.get("/")
def read_root():
    return {"message": "API DevOps com LocalStack, Kubernetes e Monitoramento rodando com sucesso!"}


@app.post("/upload")
async def upload(data: dict):
    key = data.get("key")
    value = data.get("value")

    if not key or not value:
        return {"error": "Parâmetros 'key' e 'value' são obrigatórios"}, 400

    try:
        # Salva no S3
        s3.put_object(Bucket="my-data-bucket", Key=key, Body=str(value).encode("utf-8"))

        # Salva no DynamoDB
        table.put_item(Item={"id": key, "value": value})

        return {"status": "success", "key": key, "message": "Dados salvos em S3 e DynamoDB"}
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/retrieve/{key}")
async def retrieve(key: str):
    try:
        # Primeiro tenta recuperar do DynamoDB
        response = table.get_item(Key={"id": key})
        item = response.get("Item")
        if item:
            return {"source": "DynamoDB", "key": key, "value": item["value"]}

        # Fallback: tenta recuperar do S3
        obj = s3.get_object(Bucket="my-data-bucket", Key=key)
        value = obj["Body"].read().decode("utf-8")
        return {"source": "S3", "key": key, "value": value}

    except table.exceptions.ResourceNotFoundException:
        return {"error": "Tabela DynamoDB não encontrada"}, 404
    except s3.exceptions.NoSuchKey:
        return {"error": "Chave não encontrada em S3 nem DynamoDB"}, 404
    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/health")
def health_check():
    return {"status": "healthy"}