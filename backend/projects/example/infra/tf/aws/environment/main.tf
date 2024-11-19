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
  aws_access_key     = var.aws_access_key
  aws_secret_key     = var.aws_secret_key
  aws_region         = var.aws_region
  vpc_id             = data.aws_vpc.monorepo.id
  lambda_command     = ["src.app.interactor.api.fastapi.lambda_handler.handler"]
  security_group_ids = [module.example_postgres.db_security_group_id]

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = "postgresql+psycopg2://postgres:{password}@${module.example_postgres.db_instance_endpoint}/${var.project}"
    DB_PASSWORD_SECRET_NAME = module.example_postgres.db_password_secret_name
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
  aws_access_key = var.aws_access_key
  aws_secret_key = var.aws_secret_key
  aws_region     = var.aws_region
  vpc_id         = data.aws_vpc.monorepo.id
  username       = "postgres"
}
