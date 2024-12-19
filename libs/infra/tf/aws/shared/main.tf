terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key = "monorepo-shared.tfstate"
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
  source = "../modules/codeartifact"
  project = "monorepo"
  domain = "monorepo"
}

module "monorepo_code_artifact" {
  source = "../modules/codeartifact"
  project = "monitor"
  domain = "monitor"
}

# module "monorepo_route_53_zone" {
#   source = "../modules/route53"
#   domain = "jwnwilson.co.uk"
# }