terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "jwnwilson-{{cookiecutter.project_slug}}-tf"
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

module "{{cookiecutter.project_slug}}_api" {
  source = "github.com/jwnwilson/terraform-aws-modules/modules/lambda-api"

  environment       = var.environment
  project           = "{{cookiecutter.project_slug}}"
  ecr_url           = var.ecr_url
  docker_tag        = var.docker_tag
}

module "api_gateway" {
  source = "github.com/jwnwilson/terraform-aws-modules/modules/apigateway-authorizer"

  environment       = var.environment
  lambda_invoke_arn = module.{{cookiecutter.project_slug}}_api.lambda_function_invoke_arn
  lambda_name       = module.{{cookiecutter.project_slug}}_api.lambda_function_name
  domain            = "jwnwilson.co.uk"
  api_subdomain     = "{{cookiecutter.project_slug}}-${var.environment}"
  project           = "{{cookiecutter.project_slug}}"
  authorizer_name   = "authorizer_api_gw_${var.environment}"
}