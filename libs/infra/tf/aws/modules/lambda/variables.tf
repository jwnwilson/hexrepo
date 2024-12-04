variable "aws_access_key" {}

variable "aws_secret_key" {}

variable "aws_region" {}

variable "environment" {}

variable "project" {}

variable "description" {
  default = ""
}

variable "ecr_url" {}

variable "lambda_command" {
}

variable "docker_tag" {
  default = "latest"
}

variable "vpc_id" {
  default = ""
}
variable "environment_variables"{
  default = {}
}

variable "security_group_ids" {
  default = []
}
