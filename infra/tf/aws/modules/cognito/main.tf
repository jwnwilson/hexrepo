provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

locals {
  name = var.project
}

resource "aws_cognito_user_pool" "user_pool" {
  name = var.project
  tags = var.tags
}

module "certificate" {
  source = "../acm"
  wait_for_validation = true
  names = {
    "auth.${var.domain_name}" : var.zone_id
  }
  providers = {
    aws = aws.virginia
  }
}

resource "aws_cognito_resource_server" "resource_server" {
  name         = local.name
  identifier   = "https://${var.api_subdomain}.${var.domain_name}"
  user_pool_id = "${aws_cognito_user_pool.user_pool.id}"

  scope {
    scope_name        = "all"
    scope_description = "Get access to all API Gateway endpoints."
  }
}

resource "aws_cognito_user_pool_domain" "domain" {
  domain          = "auth.${var.domain_name}"
  certificate_arn = module.certificate.arn
  user_pool_id    = aws_cognito_user_pool.user_pool.id
}

resource "aws_cognito_user_pool_client" "client" {
  name                                 = local.name
  user_pool_id                         = aws_cognito_user_pool.user_pool.id
  generate_secret                      = true
  allowed_oauth_flows                  = ["client_credentials"]
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = aws_cognito_resource_server.resource_server.scope_identifiers

  depends_on = [
    aws_cognito_user_pool.user_pool,
    aws_cognito_resource_server.resource_server,
  ]
}
