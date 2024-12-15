terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key    = "example-environment.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  db_url = "postgresql+psycopg2://postgres:{password}@${module.example_postgres.db_instance_endpoint}/${var.project}"
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

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.example_postgres.db_password_secret_arn
}

module "example_api" {
  source = "../../../../../../libs/infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  project            = "example"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.monorepo.id
  lambda_command     = ["src.app.interactor.aws.lambda_api.handler"]
  security_group_ids = [module.example_postgres.db_security_group_id]

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
  }
}

module "example_api_gateway" {
  source = "../../../../../../libs/infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.example_api.lambda_function_invoke_arn
  lambda_name       = module.example_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "example-${terraform.workspace}"
  project           = "example"
}

module "example_postgres" {
  source = "../../../../../../libs/infra/tf/aws/modules/rds"

  environment = terraform.workspace
  project     = "example"
  vpc_id      = data.aws_vpc.monorepo.id
  username    = "postgres"
}
