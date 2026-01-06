from fastapi import FastAPI
import boto3
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Configuração boto3 para LocalStack
s3 = boto3.client(
    's3',
    endpoint_url=LOCALSTACK_URL,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)

dynamodb = boto3.resource(
    'dynamodb',
    endpoint_url=LOCAL,
    aws_access_key_id='test',
    aws_secret_access_key='test'
)
table = dynamodb.Table('MyDataTable')

Instrumentator().instrument(app).expose(app)

@app.post("/upload")
async def upload(data: dict):
    key = data.get('key')
    value = data.get('value')
    # Salva no S3
    s3.put_object(Bucket='my-data-bucket', Key=key, Body=value.encode())
    # Salva no DynamoDB
    table.put_item(Item={'id': key, 'value': value})
    return {"status": "uploaded", "key": key}

@app.get("/retrieve/{key}")
async def retrieve(key: str):
    # Primeiro tenta DynamoDB
    response = table.get_item(Key={'id': key})
    item = response.get('Item')
    if item:
        return {"value": item['value']}
    # Fallback para S3
    obj = s3.get_object(Bucket='my-data-bucket', Key=key)
    value = obj['Body'].read().decode('utf-8')
    return {"value": value}