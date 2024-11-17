terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "{{cookiecutter.project_slug}}-libs.tfstate"
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

module "monorepo_code_artifact" {
  source = "./modules/codeartifact"
  project = "monorepo"
  domain = "monorepo"
}