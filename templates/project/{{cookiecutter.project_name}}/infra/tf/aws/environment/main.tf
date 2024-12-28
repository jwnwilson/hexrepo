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

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
    region = data.aws_region.current.name
}

{% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "sql" %}
locals {
  db_url = "postgresql+psycopg2://postgres:{password}@${module.{{cookiecutter.project_slug}}_postgres.db_instance_endpoint}/${var.project}"
}
{% endif %}

provider "aws" {
  region  = var.aws_region
}

data "aws_vpc" "monorepo" {
  filter {
    name   = "tag:Name"
    values = ["monorepo-vpc-${terraform.workspace}"]
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name                 = "monorepo-${var.project}"
}

{% if cookiecutter.use_db == "n" or (cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "nosql") %}
data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}
{% endif %}

module "{{cookiecutter.project_slug}}_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  project           = "{{cookiecutter.project_slug}}"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.monorepo.id
  {% if (cookiecutter.cloud_provider == "aws" and cookiecutter.use_api == "y") %}
  lambda_command    = ["src.app.interactor.aws.lambda_api.handler"]
  {% elif cookiecutter.cloud_provider == "aws" %}
  lambda_command    = ["src.app.interactor.event.aws.handler"]
  {% else %}
  lambda_command    = ["uvicorn", "app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
  {% endif %}
  {% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "sql" %}
  security_group_ids = [module.{{cookiecutter.project_slug}}_postgres.db_security_group_id]
  {% else %}
  security_group_ids = [data.aws_security_group.default_sg.id]
  {% endif %}
  {% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "nosql" %}
  # This should be modified to be restricted to all tables for this project with project_env prefix
  dynamodb_arn      = "arn:aws:dynamodb:${local.region}:${local.account_id}:table/{{cookiecutter.project_slug}}_${terraform.workspace}*"
  {% endif %}

  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = "{{ cookiecutter.cloud_provider|upper }}"
    {% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "sql" %}
    DB_URL                      = local.db_url
    DB_PASSWORD_SECRET_NAME     = data.aws_secretsmanager_secret.db_secret.name
    {% endif %}
    {% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "nosql" %}
    DB_URL                      = ""
    {% endif %}
  }
}

module "{{cookiecutter.project_slug}}_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.{{cookiecutter.project_slug}}_api.lambda_function_invoke_arn
  lambda_name       = module.{{cookiecutter.project_slug}}_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "{{cookiecutter.project_slug}}-${terraform.workspace}"
  project           = "{{cookiecutter.project_slug}}"
}

{% if cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "sql" %}
module "{{cookiecutter.project_slug}}_postgres" {
  source = "../../../../../../infra/tf/aws/modules/rds"

  environment       = terraform.workspace
  project           = "{{cookiecutter.project_slug}}"
  vpc_id            = data.aws_vpc.monorepo.id
  username          = "postgres"
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.{{cookiecutter.project_slug}}_postgres.db_password_secret_arn
}
{% elif cookiecutter.use_db == "y" and cookiecutter.use_db_logic == "nosql" %}
module "{{cookiecutter.project_slug}}_dynamodb" {
  source = "../../../../../../infra/tf/aws/modules/dynamodb"

  environment   = terraform.workspace
  table_name    = "example" 
  project       = "{{cookiecutter.project_slug}}"
}
{% endif %}

{% if cookiecutter.use_storage == "y" %}
module "{{cookiecutter.project_slug}}_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  environment = terraform.workspace
  project     = "{{cookiecutter.project_slug}}"
  name        = "example"
}
{% endif %}