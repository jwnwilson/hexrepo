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