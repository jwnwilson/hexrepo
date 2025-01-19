locals {
  name = var.project
}

resource "aws_cognito_user_pool" "user_pool" {
  name = var.project
  tags = var.tags
}

module "acm_certificate" {
  source              = "terraform-aws-modules/acm/aws"
  version             = "~> v1.0"
  domain_name         = "*.${var.domain_name}"
  zone_id             = var.zone_id
  wait_for_validation = true
  tags                = var.tags
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
  certificate_arn = "${module.acm_certificate.this_acm_certificate_arn}"
  user_pool_id    = "${aws_cognito_user_pool.user_pool.id}"
}

resource "aws_cognito_user_pool_client" "client" {
  name                                 = local.name
  user_pool_id                         = aws_cognito_user_pool.user_pool.id
  generate_secret                      = true
  allowed_oauth_flows                  = ["code", "implicit", "client_credentials"]
  supported_identity_providers         = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = [aws_cognito_resource_server.resource_server.scope_identifiers]

  depends_on = [
    "aws_cognito_user_pool.user_pool",
    "aws_cognito_resource_server.resource_server",
  ]
}
