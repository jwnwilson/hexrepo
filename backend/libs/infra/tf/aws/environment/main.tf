terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "monorepo-env.tfstate"
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

module "monorepo_vpc" {
  source = "../modules/vpc"

  environment       = terraform.workspace
  project           = "monorepo"
  aws_access_key    = var.aws_access_key
  aws_secret_key    = var.aws_secret_key
  aws_region        = var.aws_region
}