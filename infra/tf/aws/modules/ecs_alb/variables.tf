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

variable "task_cpu" {
  description = "CPU units for the task (1024 = 1 vCPU)"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory for the task in MB"
  type        = number
  default     = 512
}

variable "ecr_url" {
  description = "ECR repository URL"
  type        = string
}

variable "docker_tag" {
  description = "Docker image tag to deploy"
  type        = string
}

variable "container_command" {
  description = "Command to run in the container"
  type        = list(string)
  default     = []
}

variable "container_port" {
  description = "Port exposed by the container"
  type        = number
  default     = 8000
}

variable "environment_variables" {
  description = "Environment variables for the container"
  type        = map(string)
  default     = {}
}

variable "secrets" {
  description = "Secrets to be passed to the container"
  type        = map(string)
  default     = {}
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 1
}

variable "enable_deletion_protection" {
  description = "Whether to enable deletion protection on the ALB"
  type        = bool
  default     = false
}

variable "health_check_path" {
  description = "Path for the ALB health check"
  type        = string
  default     = "/health"
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
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

variable "security_group_ids" {
  description = "List of security group IDs for the ECS tasks"
  type        = list(string)
  default     = []
}
