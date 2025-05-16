terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  alias  = "us-east-1"
}

locals {
  name = "${var.project}-ecs-${var.environment}"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = local.name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = local.name
    Environment = var.environment
    Project     = var.project
  }
}

# Gateway Load Balancer
resource "aws_lb" "gateway" {
  name               = "${local.name}-gwlb"
  internal           = false
  load_balancer_type = "network"
  subnets            = var.private_subnet_ids

  tags = {
    Name        = "${local.name}-gwlb"
    Environment = var.environment
    Project     = var.project
  }
}

# Load Balancer Target Group
resource "aws_lb_target_group" "lb" {
  name        = "${local.name}-gwlb-tg"
  port        = var.container_port
  vpc_id      = var.vpc_id
  target_type = "ip"
  protocol    = "TCP"

  health_check {
    enabled             = true
    healthy_threshold   = 3
    interval            = 30
    protocol            = "HTTP"
    port                = "traffic-port"
    timeout             = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name        = "${local.name}-gwlb-tg"
    Environment = var.environment
    Project     = var.project
  }
}

data "aws_route53_zone" "api_zone" {
  name = var.domain_name
}

resource "aws_route53_record" "ecs" {
  name    = aws_api_gateway_domain_name.main.domain_name
  type    = "A"
  zone_id = data.aws_route53_zone.api_zone.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.main.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.main.cloudfront_zone_id
  }
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  provider          = aws.us-east-1
  domain_name       = "common-default-ecs.jwnwilson.co.uk"
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name        = "${local.name}-cert"
    Environment = var.environment
    Project     = var.project
  }
}

# Certificate Validation
resource "aws_acm_certificate_validation" "main" {
  provider                = aws.us-east-1
  certificate_arn         = aws_acm_certificate.main.arn
  validation_record_fqdns = [for record in aws_acm_certificate.main.domain_validation_options : record.resource_record_name]
}


data "aws_cognito_user_pool" "main" {
  user_pool_id = var.aws_cognito_user_pool_id
}

data "aws_cognito_user_pool_client" "main" {
  user_pool_id = var.aws_cognito_user_pool_id
  client_id    = var.aws_cognito_user_pool_client_id
}

# Update the listener to use the new certificate
resource "aws_lb_listener" "gateway" {
  load_balancer_arn = aws_lb.gateway.arn
  port              = 443
  protocol          = "TLS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.main.arn  # Use the new certificate

  # default_action {
  #   type = "authenticate-cognito"
  #   authenticate_cognito {
  #     user_pool_arn       = data.aws_cognito_user_pool.main.arn
  #     user_pool_client_id = data.aws_cognito_user_pool_client.main.id
  #     user_pool_domain    = data.aws_cognito_user_pool_domain.main.domain
  #   }
  # }
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.lb.arn
  }
}

# Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = local.name
  network_mode            = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                     = var.task_cpu
  memory                  = var.task_memory
  execution_role_arn      = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = local.name
      image     = "${var.ecr_url}:${var.docker_tag}"
      essential = true
      command   = var.container_command

      environment = [
        for k, v in var.environment_variables : {
          name  = k
          value = v
        }
      ]

      secrets = [
        for k, v in var.secrets : {
          name      = k
          valueFrom = v
        }
      ]

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${local.name}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = {
    Name        = local.name
    Environment = var.environment
    Project     = var.project
  }
}

# ECS Service
resource "aws_ecs_service" "main" {
  name            = local.name
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.lb.arn
    container_name   = local.name
    container_port   = var.container_port
  }
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  tags = {
    Name        = local.name
    Environment = var.environment
    Project     = var.project
  }

  depends_on = [
    aws_lb.gateway,
    aws_lb_target_group.lb,
    aws_lb_listener.gateway
  ]
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "main" {
  name              = "/ecs/${local.name}"
  retention_in_days = 30

  tags = {
    Name        = local.name
    Environment = var.environment
    Project     = var.project
  }
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name}-sg"
  description = "Allow inbound traffic for ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = var.container_port
    to_port         = var.container_port
    security_groups = [aws_security_group.gateway.id]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name}-sg"
    Environment = var.environment
    Project     = var.project
  }
}

# Security Group for Gateway Load Balancer
resource "aws_security_group" "gateway" {
  name        = "${local.name}-gwlb-sg"
  description = "Security group for Gateway Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    protocol        = "tcp"
    from_port       = var.container_port
    to_port         = var.container_port
    security_groups = var.api_gateway_security_group_ids
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name}-gwlb-sg"
    Environment = var.environment
    Project     = var.project
  }
}

# IAM Role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${local.name}-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:*",
        ]
        Resource = "*"
      }
    ]
  })
}

# Add permissions to access secrets
resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name = "${local.name}-execution-secrets"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "ssm:GetParameters",
          "ssm:GetParameter",
          "ssm:GetParametersByPath",
        ]
        Resource = [
          "arn:aws:secretsmanager:${var.aws_region}:${data.aws_caller_identity.current.account_id}:secret:*",
          "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:*",
          "logs:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Get current AWS account ID
data "aws_caller_identity" "current" {}

# IAM Role for ECS Task
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Auto Scaling
resource "aws_appautoscaling_target" "ecs_target" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "ecs_policy" {
  name               = "${local.name}-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs_target.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs_target.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 70.0
  }
}

# API Gateway VPC Link
resource "aws_api_gateway_vpc_link" "main" {
  name        = "${local.name}-vpc-link"
  description = "VPC Link for API Gateway to ECS"
  target_arns = [aws_lb.gateway.arn]
  tags = {
    Name        = "${local.name}-vpc-link"
    Environment = var.environment
    Project     = var.project
  }
}


# API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name        = "${local.name}-api"
  description = "API Gateway for ECS service"

  tags = {
    Name        = "${local.name}-api"
    Environment = var.environment
    Project     = var.project
  }
}

# API Gateway Resource
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "{proxy+}"
}

# API Gateway Method
resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

# API Gateway Integration
resource "aws_api_gateway_integration" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method

  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"
  connection_type         = "VPC_LINK"
  connection_id           = aws_api_gateway_vpc_link.main.id
  uri                     = "http://${aws_lb.gateway.dns_name}/{proxy}"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.proxy.id,
      aws_api_gateway_method.proxy.id,
      aws_api_gateway_integration.proxy.id
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# API Gateway Stage
resource "aws_api_gateway_stage" "main" {
  deployment_id = aws_api_gateway_deployment.main.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = var.environment

  tags = {
    Name        = "${local.name}-stage"
    Environment = var.environment
    Project     = var.project
  }
}

# API Gateway Method Settings
resource "aws_api_gateway_method_settings" "main" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled        = true
    logging_level         = "OFF"
    data_trace_enabled    = false
    throttling_rate_limit = 10000
    throttling_burst_limit = 5000
  }
}

# API Gateway Domain Name
resource "aws_api_gateway_domain_name" "main" {
  domain_name     = "${var.subdomain_name}.${var.domain_name}"
  certificate_arn = aws_acm_certificate.main.arn
}

# API Gateway Base Path Mapping
resource "aws_api_gateway_base_path_mapping" "main" {
  api_id      = aws_api_gateway_rest_api.main.id
  stage_name  = aws_api_gateway_stage.main.stage_name
  domain_name = aws_api_gateway_domain_name.main.domain_name
} 