terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "common-environment.tfstate"
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

locals {
  db_url = "postgresql+psycopg2://postgres:{password}@${module.common_postgres.db_instance_endpoint}/${var.project}"
  db_ro_url = "postgresql+psycopg2://postgres:{password}@${module.common_postgres.db_instance_ro_endpoint}/${var.project}"
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


module "common_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  name              = "${var.project}_api"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.hexrepo.id
  lambda_command    = ["src.app.interactor.aws.lambda_handler"]
  security_group_ids = [module.common_postgres.db_security_group_id]
  bucket            = module.common_bucket.bucket_name

  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = "AWS"
    DB_URL                      = local.db_url
    DB_RO_URL                   = local.db_ro_url
    DB_PASSWORD_SECRET_NAME     = data.aws_secretsmanager_secret.db_secret.name
  }
}

module "queue" {
  source = "../../../../../../infra/tf/aws/modules/sqs"

  project     = var.project
  name        = "${var.project}-${terraform.workspace}"
  environment = terraform.workspace
}

resource "aws_lambda_event_source_mapping" "queue_lambda_mapping" {
  event_source_arn = module.queue.queue_arn
  function_name    = module.common_tasks.lambda_function_name
}

module "common_tasks" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  name               = "${var.project}_tasks"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.hexrepo.id
  lambda_command     = ["src.app.interactor.event.lambda_handler"]
  security_group_ids = [module.common_postgres.db_security_group_id]

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_RO_URL               = local.db_ro_url
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
  }
}

module "common_auth" {
  source = "../../../../../../infra/tf/aws/modules/cognito"

  project     = "common"
  domain_name = var.domain
  api_subdomain  = module.common_api_gateway.api_domain
}

module "common_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.common_api.lambda_function_invoke_arn
  lambda_name       = module.common_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "common-${terraform.workspace}"
  project           = "common" 
}

module "common_postgres" {
  source = "../../../../../../infra/tf/aws/modules/rds"

  environment       = terraform.workspace
  project           = "common"
  vpc_id            = data.aws_vpc.hexrepo.id
  username          = "postgres"
  read_replica      = true
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.common_postgres.db_password_secret_arn
}

module "common_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  project     = "common"
  name        = "example"
}
