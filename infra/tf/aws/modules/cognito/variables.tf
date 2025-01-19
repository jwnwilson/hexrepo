variable "environment" {}

variable "project" {}

variable "tags" {
  default = {} 
  type = map(string)
}

variable "domain_name" {
  type = string
}

variable "api_subdomain" {
  type = string
  
}

variable "zone_id" {
  type = string
}

variable "api_gateway_id" {
  type = string
  
}