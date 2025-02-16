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

variable "callback_urls" {
  type = list(string)
  default = [ ]
}

variable "logout_urls" {
  type = list(string)
  default = [ ]
}