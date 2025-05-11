output "api_id" {
  description = "The ID of the API Gateway"
  value       = aws_apigatewayv2_api.main.id
}

output "api_endpoint" {
  description = "The endpoint of the API Gateway"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "stage_invoke_url" {
  description = "The invoke URL of the API Gateway stage"
  value       = aws_apigatewayv2_stage.main.invoke_url
}

output "domain_name" {
  description = "The domain name of the API Gateway"
  value       = aws_apigatewayv2_domain_name.main.domain_name
}

output "security_group_id" {
  description = "The ID of the security group for the API Gateway"
  value       = aws_security_group.main.id
} 