import os
from fastapi import FastAPI, HTTPException
import boto3
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="DevOps LocalStack Demo API")

# =========================================================
# CONFIGURAÇÃO DO LOCALSTACK
# =========================================================
# Em GitHub Actions / Kind → localhost funciona
# Localmente (Docker) → host.docker.internal
LOCALSTACK_URL = os.getenv("LOCALSTACK_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

AWS_CONFIG = {
    "endpoint_url": LOCALSTACK_URL,
    "aws_access_key_id": "test",
    "aws_secret_access_key": "test",
    "region_name": AWS_REGION,
}

# =========================================================
# CLIENTES AWS (LocalStack)
# =========================================================
s3 = boto3.client("s3", **AWS_CONFIG)

dynamodb = boto3.resource("dynamodb", **AWS_CONFIG)
table = dynamodb.Table("MyDataTable")

BUCKET_NAME = "my-data-bucket"

# =========================================================
# PROMETHEUS METRICS
# =========================================================
Instrumentator().instrument(app).expose(app)

# =========================================================
# ENDPOINTS
# =========================================================
@app.get("/")
def read_root():
    return {
        "message": "API DevOps com LocalStack, Kubernetes e Monitoramento rodando com sucesso!"
    }


@app.post("/upload")
async def upload(data: dict):
    key = data.get("key")
    value = data.get("value")

    if not key or value is None:
        raise HTTPException(
            status_code=400,
            detail="Parâmetros 'key' e 'value' são obrigatórios"
        )

    try:
        # Salva no S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=str(value).encode("utf-8")
        )

        # Salva no DynamoDB
        table.put_item(Item={"id": key, "value": value})

        return {
            "status": "success",
            "key": key,
            "message": "Dados salvos em S3 e DynamoDB"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrieve/{key}")
async def retrieve(key: str):
    try:
        # Tenta DynamoDB primeiro
        response = table.get_item(Key={"id": key})
        item = response.get("Item")

        if item:
            return {
                "source": "DynamoDB",
                "key": key,
                "value": item["value"]
            }

        # Fallback S3
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        value = obj["Body"].read().decode("utf-8")

        return {
            "source": "S3",
            "key": key,
            "value": value
        }

    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        raise HTTPException(status_code=404, detail="Tabela DynamoDB não encontrada")

    except s3.exceptions.NoSuchKey:
        raise HTTPException(
            status_code=404,
            detail="Chave não encontrada em S3 nem DynamoDB"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy"}

