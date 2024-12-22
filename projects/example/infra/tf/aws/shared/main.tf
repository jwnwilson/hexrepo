terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "example-shared.tfstate"
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
  source = "../../../../../../infra/tf/aws/modules/ecr"
  project           = "monorepo-${var.project}"
}

# Add url domain infra here 
