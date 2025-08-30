terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "hexrepo-jwn"
    key = "aipet_be-shared.tfstate"
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

module "main_bucket" {
  source = "../../../../../../infra/tf/aws/modules/s3"

  project     = var.project
  name        = "aipet.jwnwilson.co.uk"
}

# Add url domain infra here 
