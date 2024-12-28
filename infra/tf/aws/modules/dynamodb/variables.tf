variable "environment" {}

variable "project" {}

variable "table_name" {}

variable "tags" {
  default = {} 
  type = map(string)
}

variable "hash_key" {
  default = "id"
  type = string
}

variable "hash_key_type" {
  default = "S"
  type = string
}

variable "sort_key" {
  default = "id"
  type = string
}

variable "sort_key_type" {
  default = "S"
  type = string
}