terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}
resource "aws_kms_key" "hexrepo" {
  description = "domain key"
}

resource "aws_codeartifact_domain" "hexrepo" {
  domain         = var.domain
  encryption_key = aws_kms_key.hexrepo.arn
}

resource "aws_codeartifact_repository" "hexrepo" {
  repository = var.project
  domain     = aws_codeartifact_domain.hexrepo.domain
}

data "aws_codeartifact_repository_endpoint" "hexrepo" {
  domain     = aws_codeartifact_domain.hexrepo.domain
  repository = aws_codeartifact_repository.hexrepo.repository
  format     = "pypi"
}