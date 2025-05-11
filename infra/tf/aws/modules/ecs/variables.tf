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

variable "load_balancer_enabled" {
  description = "Whether to create a load balancer"
  type        = bool
  default     = false
}

variable "gateway_load_balancer_enabled" {
  description = "Whether to create a Gateway Load Balancer for API Gateway integration"
  type        = bool
  default     = false
}

variable "api_gateway_id" {
  description = "ID of the API Gateway to integrate with"
  type        = string
  default     = null
}

variable "api_gateway_security_group_ids" {
  description = "List of security group IDs from the API Gateway"
  type        = list(string)
  default     = []
}

variable "internal_alb" {
  description = "Whether the ALB should be internal (private) or public"
  type        = bool
  default     = false
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

variable "certificate_arn" {
  description = "ARN of the SSL certificate for HTTPS"
  type        = string
  default     = null
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