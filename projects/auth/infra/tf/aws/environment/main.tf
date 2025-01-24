terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "auth-environment.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
    region = data.aws_region.current.name
}


provider "aws" {
  region  = var.aws_region
}

data "aws_vpc" "hexrepo" {
  filter {
    name   = "tag:Name"
    values = ["hexrepo-vpc-${terraform.workspace}"]
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name                 = "hexrepo-${var.project}"
}

data "aws_security_group" "default_sg" {
  tags = {
    Name = "hexrepo-vpc-${terraform.workspace}-default"
  }
}

module "auth_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  name              = "${var.project}_api"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.hexrepo.id
  lambda_command    = ["src.app.interactor.aws.lambda_handler"]
  security_group_ids = [data.aws_security_group.default_sg.id]
  # This should be modified to be restricted to all tables for this project with project_env prefix
  dynamodb_arn      = "arn:aws:dynamodb:${local.region}:${local.account_id}:table/auth_${terraform.workspace}*"

  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = "AWS"
    DB_URL                      = ""
  }
}


module "auth_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.auth_api.lambda_function_invoke_arn
  lambda_name       = module.auth_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "auth-${terraform.workspace}"
  project           = "auth"
  auth_enabled      = false
}

module "auth_dynamodb" {
  source = "../../../../../../infra/tf/aws/modules/dynamodb"

  environment   = terraform.workspace
  table_name    = "example" 
  project       = "auth"
}

# Auth infrastructure
module "cognito" {
  source         = "../cognito"
  project        = var.project
  environment    = var.environment
  domain_name    = var.domain
  api_subdomain  = var.api_subdomain
  zone_id        = data.aws_route53_zone.api_zone.zone_id
  callback_urls  = ["https://api.${var.domain}"] 
}


