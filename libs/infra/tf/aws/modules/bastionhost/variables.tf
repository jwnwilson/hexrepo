variable "tag_application" {}

variable "subnet_id" {}

variable "bastion_host_security_group_ids" {}

variable "instance_type" {
    default = "t2.micro"
    type = string
}

variable "project" {
    type = string
}

variable "start_time" {
    default = ""
  
}

variable "stop_time" {
    default = ""
  
}