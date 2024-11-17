/* general */
variable "environment" {
  default = "develop"
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "example-service"
}

variable "ecr_api_url" {}

variable "vpc_id" {}

variable "docker_tag" {
  default = "latest"
}

variable "domain" {
  default = "example-service.link"
}

variable "api_subdomain" {
  default = "api"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "example_service_api"
}