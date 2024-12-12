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

variable "db_instance_class" {
  default = "db.t3.micro"
}

variable "start_time" {
  default = ""
}

variable "stop_time" {
  default = ""
  
}