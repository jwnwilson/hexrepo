output "cloudfront_distribution_arn" {
  value = aws_cognito_user_pool_domain.domain.cloudfront_distribution_arn
}

output "user_pool_arn" {
    value = aws_cognito_user_pool.user_pool.arn
}

output "scope_identifiers" {
    value = aws_cognito_resource_server.resource_server.scope_identifiers
}