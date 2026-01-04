# infra/terraform/variables.tf

variable "region" {
  description = "Região AWS (simulada)"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  type        = string
  default     = "my-data-bucket"
}

variable "table_name" {
  description = "Nome da tabela DynamoDB"
  type        = string
  default     = "MyDataTable"
}