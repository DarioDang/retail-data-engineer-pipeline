output "bucket_name" {
    description = "S3 bucket name"
    value = aws_s3_bucket.retail_pipeline.id
}

output "bucket_arn" {
    description = "S3 bucket ARN"
    value = aws_s3_bucket.retail_pipeline.arn
}

output "bucket_region" {
    description = "S3 bucket region"
    value = var.aws_region
}