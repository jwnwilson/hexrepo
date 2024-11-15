terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "{{cookiecutter.project_slug}}-environment.tfstate"
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

module "example_vpc" {
  source = "../../../../../../libs/infra/tf/aws/modules/vpc"

  environment       = var.environment
  project           = "example"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
}


data "aws_ecr_repository" "ecr_repo" {
  name                 = var.project
}


module "example_api" {
  source = "../../../../../../libs/infra/tf/aws/modules/lambda"

  environment       = var.environment
  project           = "example"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
  vpc_subnet_ids    = module.example_vpc.private_subnet_ids
  vpc_security_group_ids = module.example_vpc.security_group_ids
}

module "example_api_gateway" {
  source = "../../../../../../libs/infra/tf/aws/modules/apigateway"

  environment       = var.environment
  lambda_invoke_arn = module.example_api.lambda_function_invoke_arn
  lambda_name       = module.example_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "example-${var.environment}"
  project           = "example"
}

module "example_postgres" {
  source = "../../../../../../libs/infra/tf/aws/modules/rds"

  environment       = var.environment
  project           = "example"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
  vpc_id            = module.example_vpc.vpc_id
  vpc_subnet_ids    = module.example_vpc.private_subnet_ids
}