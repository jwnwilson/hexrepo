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

variable "vpc_link_id" {
  description = "VPC Link ID for ECS integration"
  type        = string
  default     = null
}

variable "vpc_id" {
  description = "VPC ID for security group"
  type        = string
}

variable "zone_id" {
  description = "Route53 hosted zone ID"
  type        = string
}