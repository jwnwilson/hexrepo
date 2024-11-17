variable "aws_access_key" {}

variable "aws_secret_key" {}

variable "aws_region" {}

variable "environment" {}

variable "project" {}

variable "username" {
  default = "postgres"
}

variable "vpc_cidr_block" {
  default = ""
}

variable "vpc_id" {
  default = ""
}

variable "vpc_subnet_ids" {
  default = ""
}

variable "vpc_private_subnet_ids" {
  default = ""
}

variable "vpc_security_group_ids" {
  default = ""
}

variable "environment_variables"{
  default = {}
}