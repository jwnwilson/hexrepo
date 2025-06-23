/* general */

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "run_be"
}

variable "docker_tag_container" {
  default = "latest"
}

variable "docker_tag_serverless" {
  default = "latest"
}

variable "domain" {
  default = ""
}

variable "api_subdomain" {
  default = "run_be"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "run_be_api"
}

