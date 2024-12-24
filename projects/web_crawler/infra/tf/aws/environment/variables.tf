/* general */

variable "aws_region" {
  default = "eu-west-1"
}

variable "aws_access_key" {
}

variable "aws_secret_key" {
}

variable "project" {
  default = "web_crawler"
}

variable "docker_tag" {
  default = "latest"
}

variable "domain" {
  default = "jwnwilson.co.uk"
}

variable "api_subdomain" {
  default = "web_crawler"
}

variable "api_repo" {
  description = "Name of container image repository"
  default     = "web_crawler_api"
}