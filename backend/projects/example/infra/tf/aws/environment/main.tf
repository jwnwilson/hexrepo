terraform {
  backend "s3" {
    region = "{{cookiecutter.aws_region}}"
    bucket = "monorepo-{{cookiecutter.project_slug}}-tf"
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

module "{{cookiecutter.project_slug}}_vpc" {
  source = "../../../../../../libs/infra/tf/aws/modules/vpc"

  environment       = var.environment
  project           = "{{cookiecutter.project_slug}}"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
}


module "{{cookiecutter.project_slug}}_api" {
  source = "../../../../../libs/infra/tf/aws/modules/lambda"

  environment       = var.environment
  project           = "{{cookiecutter.project_slug}}"
  ecr_url           = var.ecr_url
  docker_tag        = var.docker_tag
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
  vpc_subnet_ids    = module.{{cookiecutter.project_slug}}_vpc.private_subnet_ids
  vpc_security_group_ids = module.{{cookiecutter.project_slug}}_vpc.security_group_ids
}

module "{{cookiecutter.project_slug}}_api_gateway" {
  source = "../../../../../libs/infra/tf/aws/modules/apigateway"

  environment       = var.environment
  lambda_invoke_arn = module.example_api.lambda_function_invoke_arn
  lambda_name       = module.example_api.lambda_function_name
  domain            = "{{cookiecutter.domain}}"
  api_subdomain     = "{{cookiecutter.project_slug}}-${var.environment}"
  project           = "{{cookiecutter.project_slug}}"
  authorizer_name   = "authorizer_api_gw_${var.environment}"
}

module "{{cookiecutter.project_slug}}_postgres" {
  source = "../../../../../libs/infra/tf/aws/modules/rds"

  environment       = var.environment
  project           = "{{cookiecutter.project_slug}}"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
  vpc_id            = module.{{cookiecutter.project_slug}}_vpc.vpc_id
  vpc_subnet_ids    = module.{{cookiecutter.project_slug}}_vpc.private_subnet_ids
}