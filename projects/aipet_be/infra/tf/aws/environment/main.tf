terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "aipet_be-environment.tfstate"
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
    db_url            = "postgresql+psycopg://postgres:{password}@${module.postgres.db_instance_endpoint}/${var.project}"
    db_ro_url         = module.postgres.db_instance_ro_endpoint != null ? "postgresql+psycopg://postgres:{password}@${module.postgres.db_instance_ro_endpoint}/${var.project}" : "postgresql+psycopg://postgres:{password}@${module.postgres.db_instance_endpoint}/${var.project}"
    api_subdomain     = "${var.project}-${terraform.workspace}"
    api_subdomain_ecs = "${var.project}-${terraform.workspace}-ecs"
    app_url           = "https://${local.api_subdomain}.${var.domain}"
    common_env_vars = {
      ENVIRONMENT             = terraform.workspace
      PROJECT                 = var.project
      CLOUD_PROVIDER          = "AWS"
      DB_URL                  = local.db_url
      DB_RO_URL               = local.db_ro_url
      READ_REPLICA_ENABLED    = "false"
      DB_PASSWORD_SECRET_NAME = data.aws_secretsmanager_secret.db_secret.name
      TASK_QUEUE              = "${var.project}_${terraform.workspace}_tasks"
      ALLOWED_ORIGINS         = "*"
      LOG_JSON                = "true"
      ORIGIN_URL              = "https://${local.api_subdomain_ecs}.${var.domain}"
      LOG_LEVEL               = "INFO"
    }
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
  name                 = "hexrepo-${var.project}_be"
}

module "alb" {
  source = "../../../../../../infra/tf/aws/modules/alb"

  project            = var.project
  environment        = terraform.workspace
  aws_region         = var.aws_region
  vpc_id             = data.aws_vpc.hexrepo.id
  private_subnet_ids = data.aws_subnets.private.ids
  public_subnet_ids  = data.aws_subnets.public.ids
  vpc_cidr_blocks    = [data.aws_vpc.hexrepo.cidr_block]
  container_port     = 8000
  domain_name        = var.domain
  subdomain_name     = local.api_subdomain_ecs
  enabled            = true
  health_check_path  = "/api/v1/health"
}

module "aipet_be_ecs_api" {
  source             = "../../../../../../infra/tf/aws/modules/ecs"
  project            = var.project
  name               = "api"
  environment        = terraform.workspace
  aws_region         = var.aws_region
  vpc_id             = data.aws_vpc.hexrepo.id
  private_subnet_ids = data.aws_subnets.private.ids
  security_group_ids = [module.postgres.db_security_group_id]
  target_group_arn   = module.alb.target_group_arn
  # This costs money
  container_insights = "disabled"
  min_capacity       = 0

  ecr_url        = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag     = var.docker_tag_container
  container_port = 8000

  environment_variables = local.common_env_vars
  secrets = {
    DB_PASSWORD = data.aws_secretsmanager_secret.db_secret.arn
  }

  desired_count = 1
  task_cpu      = 256
  task_memory   = 512
}

module "postgres" {
  source = "../../../../../../infra/tf/aws/modules/rds"

  environment       = terraform.workspace
  project           = var.project
  vpc_id            = data.aws_vpc.hexrepo.id
  username          = "postgres"
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.postgres.db_password_secret_arn
}

module "main_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  project     = var.project
  name        = "aipet-files"
}
