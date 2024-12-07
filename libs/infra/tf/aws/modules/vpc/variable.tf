variable "aws_access_key" {}

variable "aws_secret_key" {}

variable "aws_region" {}

variable "environment" {}

variable "project" {}

variable "nat_gateway" {
    type = bool
    default = false
}

variable "fck_nat_gateway" {
    type = bool
    default = false
  
}

variable "nat_start_time" {
    default = ""
  
}

variable "nat_stop_time" {
    default = ""
  
}