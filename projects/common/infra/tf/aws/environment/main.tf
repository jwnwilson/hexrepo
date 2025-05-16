terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key    = "common-environment.tfstate"
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
  account_id        = data.aws_caller_identity.current.account_id
  region            = data.aws_region.current.name
  db_url            = "postgresql+psycopg://postgres:{password}@${module.common_postgres.db_instance_endpoint}/${var.project}"
  db_ro_url         = module.common_postgres.db_instance_ro_endpoint != null ? "postgresql+psycopg://postgres:{password}@${module.common_postgres.db_instance_ro_endpoint}/${var.project}" : "postgresql+psycopg://postgres:{password}@${module.common_postgres.db_instance_endpoint}/${var.project}"
  api_subdomain     = "common-${terraform.workspace}"
  api_subdomain_ecs = "common-${terraform.workspace}-ecs"
  app_url           = "https://${local.api_subdomain}.${var.domain}"
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "hexrepo" {
  filter {
    name   = "tag:Name"
    values = ["hexrepo-vpc-${terraform.workspace}"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.hexrepo.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*private*"]
  }
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.hexrepo.id]
  }

  filter {
    name   = "tag:Name"
    values = ["*public*"]
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name = "hexrepo-${var.project}"
}

data "aws_route53_zone" "main" {
  name = var.domain
}

module "common_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  name               = "${var.project}_api"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.hexrepo.id
  lambda_command     = ["src.app.interactor.api.lambda_handler"]
  security_group_ids = [module.common_postgres.db_security_group_id]
  bucket             = module.common_bucket.bucket_name
  keep_warm_schedule = "cron(* 09-17 * * ? *)"

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_RO_URL               = local.db_ro_url
    READ_REPLICA_ENABLED    = "false"
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
    TASK_QUEUE              = "${var.project}_${terraform.workspace}_tasks"
    CLIENT_ID               = module.common_auth.client_id
    USER_POOL_ID            = module.common_auth.user_pool_id
  }
}

module "common_ecs_api" {
  source = "../../../../../../infra/tf/aws/modules/ecs"

  project            = var.project
  environment        = terraform.workspace
  aws_region         = var.aws_region
  vpc_id             = data.aws_vpc.hexrepo.id
  private_subnet_ids = data.aws_subnets.private.ids
  public_subnet_ids  = data.aws_subnets.public.ids
  vpc_cidr_blocks    = [data.aws_vpc.hexrepo.cidr_block]

  ecr_url    = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag = var.docker_tag

  container_command = ["src.app.interactor.api.app:app"]
  container_port    = 8000

  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_RO_URL               = local.db_ro_url
    READ_REPLICA_ENABLED    = "false"
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
    TASK_QUEUE              = "${var.project}_${terraform.workspace}_tasks"
    CLIENT_ID               = module.common_auth.client_id
    USER_POOL_ID            = module.common_auth.user_pool_id
  }

  secrets = {
    DB_PASSWORD = data.aws_secretsmanager_secret.db_secret.arn
  }

  desired_count = 1
  task_cpu      = 512
  task_memory   = 1024

  # api_gateway_id                  = module.common_api_gateway_ecs.api_id
  # api_gateway_security_group_ids  = [module.common_api_gateway_ecs.security_group_id]
  # certificate_arn                 = module.common_api_gateway_ecs.certificate_arn
  aws_cognito_user_pool_id        = module.common_auth.user_pool_id
  aws_cognito_user_pool_client_id = module.common_auth.client_id
  domain_name                     = var.domain
  subdomain_name                  = local.api_subdomain_ecs
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
  keep_warm_schedule = ""
  environment_variables = {
    ENVIRONMENT             = terraform.workspace
    CLOUD_PROVIDER          = "AWS"
    DB_URL                  = local.db_url
    DB_RO_URL               = local.db_ro_url
    READ_REPLICA_ENABLED    = "false"
    DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
    TASK_QUEUE              = "${var.project}_${terraform.workspace}_tasks"
    CLIENT_ID               = module.common_auth.client_id
    USER_POOL_ID            = module.common_auth.user_pool_id
  }
}

module "common_auth" {
  source = "../../../../../../infra/tf/aws/modules/cognito"

  project       = "common"
  domain_name   = var.domain
  api_subdomain = local.api_subdomain
  callback_urls = [local.app_url]
}

module "common_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment           = terraform.workspace
  lambda_invoke_arn     = module.common_api.lambda_function_invoke_arn
  lambda_name           = module.common_api.lambda_function_name
  domain                = var.domain
  api_subdomain         = local.api_subdomain
  project               = "common"
  cognito_user_pool_arn = module.common_auth.user_pool_arn
  # Auth handled in api middleware
  auth_enabled = false
}

# module "common_api_gateway_ecs" {
#   source = "../../../../../../infra/tf/aws/modules/apigateway_ecs"

#   environment   = terraform.workspace
#   domain        = var.domain
#   api_subdomain = local.api_subdomain_ecs
#   project       = "common"
#   vpc_id        = data.aws_vpc.hexrepo.id
#   vpc_link_id   = module.common_ecs_api.vpc_link_id
#   zone_id       = data.aws_route53_zone.main.zone_id
#   aws_lb_listener_arn = module.common_ecs_api.aws_lb_listener_arn
# }

module "common_postgres" {
  source = "../../../../../../infra/tf/aws/modules/rds"

  environment  = terraform.workspace
  project      = "common"
  vpc_id       = data.aws_vpc.hexrepo.id
  username     = "postgres"
  read_replica = false
  start_time   = "09:00:00"
  stop_time    = "17:00:00"
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.common_postgres.db_password_secret_arn
}

module "common_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  project = "common"
  name    = "example"
}
