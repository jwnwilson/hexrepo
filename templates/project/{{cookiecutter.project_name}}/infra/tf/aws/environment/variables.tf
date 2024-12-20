/* general */

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "{{cookiecutter.project_slug}}"
}

variable "docker_tag" {
  default = "latest"
}

variable "domain" {
  default = "{{cookiecutter.api_domain}}"
}

variable "api_subdomain" {
  default = "{{cookiecutter.project_slug}}"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "{{cookiecutter.project_slug}}_api"
}