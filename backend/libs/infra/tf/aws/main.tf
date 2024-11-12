terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
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

resource "aws_kms_key" "monorepo" {
  description = "domain key"
}

resource "aws_codeartifact_domain" "monorepo" {
  domain         = "monorepo"
  encryption_key = aws_kms_key.monorepo.arn
}

resource "aws_codeartifact_repository" "monorepo" {
  repository = "monorepo"
  domain     = aws_codeartifact_domain.monorepo.domain
}

data "aws_codeartifact_repository_endpoint" "monorepo" {
  domain     = aws_codeartifact_domain.monorepo.domain
  repository = aws_codeartifact_repository.monorepo.repository
  format     = "pypi"
}