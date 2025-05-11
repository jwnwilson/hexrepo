terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

data "aws_route53_zone" "api_zone" {
  name = var.domain
}

resource "aws_route53_record" "this" {
  name    = aws_api_gateway_domain_name.this.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.api_zone.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.this.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.this.cloudfront_zone_id
  }
}

resource "aws_acm_certificate" "api_cert" {
  domain_name       = "${var.api_subdomain}.${var.domain}"
  validation_method = "DNS"
  provider          = aws.virginia

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "api_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api_cert.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.api_zone.zone_id
}

resource "aws_acm_certificate_validation" "api_cert_validation" {
  provider                = aws.virginia
  certificate_arn         = aws_acm_certificate.api_cert.arn
  validation_record_fqdns = [for record in aws_route53_record.api_cert_validation : record.fqdn]
}


resource "aws_api_gateway_stage" "this" {
  deployment_id         = aws_api_gateway_deployment.apideploy.id
  rest_api_id           = aws_api_gateway_rest_api.apiLambda.id
  stage_name            = var.environment
  cache_cluster_enabled = false
  cache_cluster_size    = "0.5"
  xray_tracing_enabled  = true
}

resource "aws_api_gateway_domain_name" "this" {
  certificate_arn = aws_acm_certificate_validation.api_cert_validation.certificate_arn
  domain_name     = "${var.api_subdomain}.${var.domain}"
}

resource "aws_api_gateway_base_path_mapping" "example" {
  api_id      = aws_api_gateway_rest_api.apiLambda.id
  stage_name  = aws_api_gateway_stage.this.stage_name
  domain_name = aws_api_gateway_domain_name.this.domain_name
}

resource "aws_api_gateway_rest_api" "apiLambda" {
  name        = "${var.project}_${var.environment}"
  description = "${var.project} API"
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.apiLambda.id

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"
}

output "base_url" {
  value = aws_api_gateway_deployment.apideploy.invoke_url
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "{proxy+}"
}


resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = var.auth_enabled ? aws_api_gateway_method.proxyMethod_auth[0].resource_id : aws_api_gateway_method.proxyMethod_no_auth[0].resource_id
  http_method = var.auth_enabled ? aws_api_gateway_method.proxyMethod_auth[0].http_method : aws_api_gateway_method.proxyMethod_no_auth[0].http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


# Auth infrastructure
resource "aws_api_gateway_authorizer" "authorizer" {
  count         = var.auth_enabled ? 1 : 0
  name          = var.project
  type          = "COGNITO_USER_POOLS"
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  provider_arns = [var.cognito_user_pool_arn]
}

resource "aws_api_gateway_method" "proxyMethod_auth" {
  count                = var.auth_enabled ? 1 : 0
  rest_api_id          = aws_api_gateway_rest_api.apiLambda.id
  resource_id          = aws_api_gateway_resource.proxy.id
  http_method          = "ANY"
  authorization        = "COGNITO_USER_POOLS"
  authorizer_id        = aws_api_gateway_authorizer.authorizer[0].id
  authorization_scopes = var.cognito_scope_identifiers
}

# No Auth
resource "aws_api_gateway_method" "proxyMethod_no_auth" {
  count         = var.auth_enabled ? 0 : 1
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

locals {
  name = "${var.project}-${var.environment}"
}

# API Gateway
resource "aws_apigatewayv2_api" "main" {
  name          = local.name
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["*"]
  }
}

# API Gateway Stage
resource "aws_apigatewayv2_stage" "main" {
  api_id = aws_apigatewayv2_api.main.id
  name   = terraform.workspace
  auto_deploy = true
}

# API Gateway Integration
resource "aws_apigatewayv2_integration" "main" {
  api_id           = aws_apigatewayv2_api.main.id
  integration_type = var.vpc_link_id != null ? "HTTP_PROXY" : "AWS_PROXY"

  dynamic "lambda_integration" {
    for_each = var.vpc_link_id == null ? [1] : []
    content {
      lambda_invoke_arn = var.lambda_invoke_arn
    }
  }

  dynamic "http_integration" {
    for_each = var.vpc_link_id != null ? [1] : []
    content {
      connection_id    = var.vpc_link_id
      connection_type  = "VPC_LINK"
      description      = "HTTP integration with ECS"
      integration_method = "ANY"
      integration_uri  = "http://${var.vpc_link_id}"
    }
  }
}

# API Gateway Route
resource "aws_apigatewayv2_route" "main" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.main.id}"
}

# API Gateway Domain Name
resource "aws_apigatewayv2_domain_name" "main" {
  domain_name = "${var.api_subdomain}.${var.domain}"

  domain_name_configuration {
    certificate_arn = var.certificate_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

# API Gateway Domain Name API Mapping
resource "aws_apigatewayv2_api_mapping" "main" {
  api_id      = aws_apigatewayv2_api.main.id
  domain_name = aws_apigatewayv2_domain_name.main.id
  stage       = aws_apigatewayv2_stage.main.id
}

# Route53 Record
resource "aws_route53_record" "main" {
  name    = aws_apigatewayv2_domain_name.main.domain_name
  type    = "A"
  zone_id = var.zone_id

  alias {
    name                   = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.main.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

# Security Group for API Gateway
resource "aws_security_group" "main" {
  name        = "${local.name}-sg"
  description = "Security group for API Gateway"
  vpc_id      = var.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name}-sg"
    Environment = var.environment
    Project     = var.project
  }
}

