terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "{{cookiecutter.project_slug}}-shared.tfstate"
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

module "{{cookiecutter.project_slug}}_ecr" {
  source = "../../../../../../libs/infra/tf/aws/modules/ecr"
  project           = "monorepo-${var.project}"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
}

# Add url domain infra here 
