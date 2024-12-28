/* general */
variable "environment" {
  default = "develop"
}

variable "aws_region" {
  default = "eu-west-1"
}

variable "region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "nosql"
}

variable "docker_tag" {
  default = "latest"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "nosql_api"
}