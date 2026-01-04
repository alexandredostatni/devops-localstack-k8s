output "bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "table_name" {
  value = aws_dynamodb_table.data_table.name
}