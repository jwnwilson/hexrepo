terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "run_be-environment.tfstate"
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
  db_url = "postgresql+psycopg://postgres:{password}@${module.run_be_postgres.db_instance_endpoint}/${var.project}"
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



module "run_be_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  name              = "${var.project}_api"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.hexrepo.id
  
  lambda_command    = ["uvicorn", "app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
  
  
  security_group_ids = [module.run_be_postgres.db_security_group_id]
  
  
  
  bucket            = module.run_be_bucket.bucket_name
  

  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = ""
    
    DB_URL                      = local.db_url
    DB_RO_URL                   = local.db_ro_url
    READ_REPLICA_ENABLED        = "false"
    DB_PASSWORD_SECRET_NAME     = data.aws_secretsmanager_secret.db_secret.name
    
    
    
    TASK_QUEUE              = "${var.project}_${terraform.workspace}_tasks"
    
    CLIENT_ID               = module.common_auth.client_id
    USER_POOL_ID            = module.common_auth.user_pool_id
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
  function_name    = module.example_tasks.lambda_function_name
}

module "example_tasks" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  name               = "${var.project}_tasks"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.hexrepo.id
  lambda_command     = ["src.app.interactor.event.lambda_handler"]
  security_group_ids = [module.example_postgres.db_security_group_id]

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_RO_URL               = local.db_ro_url
    READ_REPLICA_ENABLED    = "false"
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
  }
}


module "run_be_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.run_be_api.lambda_function_invoke_arn
  lambda_name       = module.run_be_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "run_be-${terraform.workspace}"
  project           = "run_be"
  cognito_user_pool_arn = module.common_auth.user_pool_arn
  # Auth handled in api middleware
  auth_enabled          = false
}


module "run_be_postgres" {
  source = "../../../../../../infra/tf/aws/modules/rds"

  environment       = terraform.workspace
  project           = "run_be"
  vpc_id            = data.aws_vpc.hexrepo.id
  username          = "postgres"
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.run_be_postgres.db_password_secret_arn
}



module "run_be_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  environment = terraform.workspace
  project     = "run_be"
  name        = "example"
}
