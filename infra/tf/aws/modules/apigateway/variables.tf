variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "domain" {
  description = "Domain name for the API"
  type        = string
}

variable "api_subdomain" {
  description = "Subdomain for the API"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Lambda function invoke ARN"
  type        = string
  default     = null
}

variable "lambda_name" {
  description = "Lambda function name"
  type        = string
  default     = null
}

variable "vpc_link_id" {
  description = "VPC Link ID for ECS integration"
  type        = string
  default     = null
}

variable "vpc_id" {
  description = "VPC ID for security group"
  type        = string
}

variable "certificate_arn" {
  description = "ARN of the SSL certificate"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "Cognito User Pool ARN"
  type        = string
  default     = null
}

variable "auth_enabled" {
  description = "Whether to enable Cognito authentication"
  type        = bool
  default     = false
}

variable "cognito_scope_identifiers" {
  type = list(string)
  default = [] 
}
