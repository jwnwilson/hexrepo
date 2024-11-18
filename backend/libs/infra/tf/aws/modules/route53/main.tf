provider "aws" {
  alias = "virginia"
  region = "us-east-1"
}

resource "aws_route53_zone" "monorepo" {
  name = var.domain
}