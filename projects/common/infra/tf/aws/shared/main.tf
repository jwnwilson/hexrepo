terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "common-shared.tfstate"
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

module "common_ecr_container" {
  source = "../../../../../../infra/tf/aws/modules/ecr"
  project           = "hexrepo-${var.project}"
}

module "common_ecr_lambda" {
  source = "../../../../../../infra/tf/aws/modules/ecr"
  project           = "hexrepo-${var.project}-lambda"
}

# Add url domain infra here 
