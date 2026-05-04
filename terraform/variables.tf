variable "aws_region" {
    description = "AWS region"
    type = string
    default = "ap-southeast-2"
}

variable "bucket_name" {
    description = "S3 bucket name for retail price intelligence"
    type = string
    default = "dario-retail-price-pipeline"
}

variable "environment" {
    description = "Environment name"
    type = string 
    default = "dev"
}
