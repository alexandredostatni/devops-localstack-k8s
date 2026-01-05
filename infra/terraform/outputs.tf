output "bucket_name" {
  value = aws_s3_bucket.test.bucket
}

output "table_name" {
  value = aws_dynamodb_table.data_table.name
}