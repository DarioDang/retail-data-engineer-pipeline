terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Bucket 
resource "aws_s3_bucket" "retail_pipeline" {
  bucket = var.bucket_name

  tags = {
    Project = "retail-price-pipeline"
    Environment = var.environment
    ManagedBy = "terraform"
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "retail_pipeline" {
  bucket = aws_s3_bucket.retail_pipeline.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning 
resource "aws_s3_bucket_versioning" "retail_pipeline" {
  bucket = aws_s3_bucket.retail_pipeline.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Folder structure (raw layer)
resource "aws_s3_object" "raw_shopping" {
  bucket  = aws_s3_bucket.retail_pipeline.id
  key     = "raw/shopping/"
  content = ""
}