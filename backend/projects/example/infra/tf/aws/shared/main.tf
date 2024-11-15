terraform {
  backend "s3" {
    region = "{{cookiecutter.aws_region}}"
    bucket = "monorepo-{{cookiecutter.project_slug}}-tf"
    key = "terraform.tfstate"
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

module "example_ecr" {
  source = "../../../../../libs/infra/tf/aws/modules/ecr"
  project           = "example"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
}

# Add url domain infra here 
