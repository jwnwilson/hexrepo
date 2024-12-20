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

{% if cookiecutter.use_db == "y" %}
locals {
  db_url = "postgresql+psycopg2://postgres:{password}@${module.example_postgres.db_instance_endpoint}/${var.project}"
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

{% if cookiecutter.use_db == "n" %}
data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}
{% endif %}

module "example_api" {
  source = "../../../../../../libs/infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  project           = "{{cookiecutter.project_slug}}"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.monorepo.id
  {% if cookiecutter.cloud_provider == "aws" and cookiecutter.use_api %}
  lambda_command    = ["src.app.interactor.api.lambda.handler"]
  {% elif cookiecutter.cloud_provider == "aws" %}
    lambda_command    = ["src.app.interactor.event.lambda.handler"]
  {% else %}
  lambda_command    = ["uvicorn", "app.interactor.api.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
  {% endif %}
  {% if cookiecutter.use_db == "y" %}
  security_group_ids = [module.example_postgres.db_security_group_id]
  {% else %}
  security_group_ids = [data.aws_security_group.default_sg.id]
  {% endif %}


  
  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = "{{ cookiecutter.cloud_provider|upper }}"
    {% if cookiecutter.use_db == "y" %}
    DB_URL                      = local.db_url
    DB_PASSWORD_SECRET_NAME     = data.aws_secretsmanager_secret.db_secret.name
    {% endif %}
  }
}

module "example_api_gateway" {
  source = "../../../../../../libs/infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.example_api.lambda_function_invoke_arn
  lambda_name       = module.example_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "{{cookiecutter.project_slug}}-${terraform.workspace}"
  project           = "{{cookiecutter.project_slug}}"
}

{% if cookiecutter.use_db == "y" %}
module "example_postgres" {
  source = "../../../../../../libs/infra/tf/aws/modules/rds"

  environment       = terraform.workspace
  project           = "{{cookiecutter.project_slug}}"
  vpc_id            = data.aws_vpc.monorepo.id
  username          = "postgres"
}

data "aws_secretsmanager_secret" "db_secret" {
  arn = module.example_postgres.db_password_secret_arn
}
{% endif %}