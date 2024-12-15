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
    DB_URL_SECRET_NAME = data.example_postgres.db_url_secret_name
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

  environment    = terraform.workspace
  project        = "example"
  vpc_id         = data.aws_vpc.monorepo.id
  username       = "postgres"
}
