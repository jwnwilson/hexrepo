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

variable "lambda_schedule_expression" {
  default = null
}

variable "dynamodb_arn" {
  default = "*"
  type = string
  
}

variable "bucket" {
  type = string
}