terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}
provider "aws" {
  alias = "virginia"
  region = "us-east-1"
}

resource "aws_route53_zone" "hexrepo" {
  name = var.domain
}