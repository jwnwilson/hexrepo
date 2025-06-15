/* general */

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "run"
}

variable "docker_tag" {
  default = "latest"
}

variable "domain" {
  default = ""
}

variable "api_subdomain" {
  default = "run"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "run_api"
}