variable "lambda_invoke_arn" {}

variable "lambda_name" {}

variable "environment" {}

variable "project" {}

variable "domain" {}

variable "api_subdomain" {}

variable "auth_enabled" {
  type = bool
  default = true
}

variable "cognito_user_pool_arn" {
    type = string
    default = ""
}

variable "cognito_scope_identifiers" {
  type = list(string)
  default = [] 
}
