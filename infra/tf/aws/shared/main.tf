terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "hexrepo-shared.tfstate"
    dynamodb_table = "terraform-state-lock-dynamo"
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

module "hexrepo_code_artifact" {
  source = "../modules/codeartifact"
  project = "hexrepo"
  domain = "hexrepo"
}

# module "hexrepo_route_53_zone" {
#   source = "../modules/route53"
#   domain = "jwnwilson.co.uk"
# }