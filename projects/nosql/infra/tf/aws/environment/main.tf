terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key    = "nosql-environment.tfstate"
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
  region = var.aws_region
}

data "aws_vpc" "monorepo" {
  filter {
    name   = "tag:Name"
    values = ["monorepo-vpc-${terraform.workspace}"]
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name = "monorepo-${var.project}"
}

data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}

module "nosql_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  project            = "nosql"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.monorepo.id
  lambda_command     = ["src.app.interactor.aws.lambda_api.handler"]
  security_group_ids = [data.aws_security_group.default_sg.id]
  dynamodb_arn       = "arn:aws:dynamodb:${local.region}:${local.account_id}:table/nosql_${terraform.workspace}*"

  environment_variables = {
    ENVIRONMENT    = terraform.workspace
    CLOUD_PROVIDER = "AWS"
    DB_URL         = ""
  }
}

module "nosql_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.nosql_api.lambda_function_invoke_arn
  lambda_name       = module.nosql_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "nosql-${terraform.workspace}"
  project           = "nosql"
}

module "nosql_dynamodb" {
  source = "../../../../../../infra/tf/aws/modules/dynamodb"

  environment   = terraform.workspace
  table_name    = "example" 
  project       = "nosql"
}
