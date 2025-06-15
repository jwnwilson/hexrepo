variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ECS cluster will be created"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for the ECS tasks"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the ALB"
  type        = list(string)
  default     = []
}

variable "vpc_cidr_blocks" {
  description = "List of VPC CIDR blocks for internal ALB access"
  type        = list(string)
  default     = []
}

variable "container_port" {
  description = "Port on which the container is listening"
  type        = number
}

variable "domain_name" {
  description = "Domain name for the API Gateway"
  type        = string
  default     = "jwnwilson.co.uk"
}

variable "subdomain_name" {
  description = "Subdomain name for the API Gateway"
  type        = string
  default     = "ecs"
}
