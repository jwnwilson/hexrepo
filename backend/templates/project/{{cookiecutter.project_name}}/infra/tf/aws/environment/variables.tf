/* general */

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "example"
}

variable "docker_tag" {
  default = "latest"
}

variable "domain" {
  default = "jwnwilson.co.uk"
}

variable "api_subdomain" {
  default = "example"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "example_service_api"
}