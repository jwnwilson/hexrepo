terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key    = "monitor-environment.tfstate"
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

data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name = "monorepo-${var.project}"
}

module "example_api" {
  source = "../../../../../../libs/infra/tf/aws/modules/lambda"

  environment        = terraform.workspace
  project            = "monitor"
  ecr_url            = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag         = var.docker_tag
  vpc_id             = data.aws_vpc.monorepo.id
  lambda_command     = ["src.app.interactor.aws.lambda_api.handler"]
  security_group_ids = [data.aws_security_group.default_sg.id]

  environment_variables = {
    ENVIRONMENT    = terraform.workspace
    CLOUD_PROVIDER = "AWS"
  }
}
