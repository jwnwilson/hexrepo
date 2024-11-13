terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "jwnwilson-example-tf"
    key = "terraform.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region  = var.aws_region
}

module "example_api" {
  source = "github.com/jwnwilson/terraform-aws-modules/modules/lambda-api"

  environment       = var.environment
  project           = "example"
  ecr_url           = var.ecr_url
  docker_tag        = var.docker_tag
}

module "api_gateway" {
  source = "github.com/jwnwilson/terraform-aws-modules/modules/apigateway-authorizer"

  environment       = var.environment
  lambda_invoke_arn = module.example_api.lambda_function_invoke_arn
  lambda_name       = module.example_api.lambda_function_name
  domain            = "jwnwilson.co.uk"
  api_subdomain     = "example-${var.environment}"
  project           = "example"
  authorizer_name   = "authorizer_api_gw_${var.environment}"
}