terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "web_crawler-environment.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}


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

data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}

module "web_crawler_api" {
  source = "../../../../../../infra/tf/aws/modules/lambda"

  environment       = terraform.workspace
  project           = "web_crawler"
  ecr_url           = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag        = var.docker_tag
  vpc_id            = data.aws_vpc.monorepo.id
  lambda_command    = ["src.app.interactor.aws.lambda_api.handler"]
  security_group_ids = [data.aws_security_group.default_sg.id]


  
  environment_variables = {
    ENVIRONMENT                 = terraform.workspace
    CLOUD_PROVIDER              = "AWS"
  }
}

module "web_crawler_api_gateway" {
  source = "../../../../../../infra/tf/aws/modules/apigateway"

  environment       = terraform.workspace
  lambda_invoke_arn = module.web_crawler_api.lambda_function_invoke_arn
  lambda_name       = module.web_crawler_api.lambda_function_name
  domain            = var.domain
  api_subdomain     = "web_crawler-${terraform.workspace}"
  project           = "web_crawler"
}

