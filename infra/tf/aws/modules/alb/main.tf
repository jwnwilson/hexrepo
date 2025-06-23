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

resource "aws_s3_bucket" "lb_logs" {
  bucket = "${local.name}-alb-logs"
}

# Get the ALB account ID for the current region
data "aws_elb_service_account" "main" {}

resource "aws_s3_bucket_policy" "lb_logs" {
  bucket = aws_s3_bucket.lb_logs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_elb_service_account.main.id}:root"
        }
        Action = [
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.lb_logs.arn}/*"
      }
    ]
  })
}


# Appliacation Load Balancer
resource "aws_lb" "main" {
  count              = var.enabled ? 1 : 0
  name               = "${local.name}-alb"
  load_balancer_type = "application"
  internal           = false
  subnets            = var.public_subnet_ids
  security_groups    = [aws_security_group.lb[0].id]

  access_logs {
    bucket  = aws_s3_bucket.lb_logs.id
    prefix  = "${local.name}-alb"
    enabled = true
  }

  tags = {
    Name        = "${local.name}-alb"
    Environment = var.environment
    Project     = var.project
  }
}

# Load Balancer Target Group
resource "aws_lb_target_group" "lb" {
  count       = var.enabled ? 1 : 0
  name        = "${local.name}-alb-tg"
  port        = var.container_port
  vpc_id      = var.vpc_id
  target_type = "ip"
  protocol    = "HTTP"

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
    Name        = "${local.name}-alb-tg"
    Environment = var.environment
    Project     = var.project
  }
}

# Update the listener to use the new certificate
resource "aws_lb_listener" "http" {
  count             = var.enabled ? 1 : 0
  load_balancer_arn = aws_lb.main[0].arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = var.enabled ? 1 : 0
  load_balancer_arn = aws_lb.main[0].arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.main[0].arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.lb[0].arn
  }

  depends_on = [
    aws_acm_certificate_validation.main,
    aws_lb.main
  ]
}

data "aws_route53_zone" "api_zone" {
  name = var.domain_name
}

resource "aws_route53_record" "ecs_cname" {
  count   = var.enabled ? 1 : 0
  zone_id = data.aws_route53_zone.api_zone.id
  name    = "${var.subdomain_name}.${var.domain_name}"
  type    = "CNAME"
  ttl     = "60"
  records = [aws_lb.main[0].dns_name]
}

# ACM Certificate
resource "aws_acm_certificate" "main" {
  count             = var.enabled ? 1 : 0
  # provider = aws.us-east-1
  domain_name       = "${var.subdomain_name}.${var.domain_name}"
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
  count             = var.enabled ? 1 : 0
  # provider = aws.us-east-1
  certificate_arn         = aws_acm_certificate.main[0].arn
  validation_record_fqdns = [for record in aws_acm_certificate.main[0].domain_validation_options : record.resource_record_name]

  depends_on = [
    aws_route53_record.ecs_cname
  ]
}

# Security Group for Gateway Load Balancer
resource "aws_security_group" "lb" {
  count       = var.enabled ? 1 : 0
  name        = "${local.name}-alb-sg"
  description = "Security group for Gateway Load Balancer"
  vpc_id      = var.vpc_id

  ingress {
    protocol    = "tcp"
    from_port   = 80
    to_port     = 80
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    protocol    = "tcp"
    from_port   = 443
    to_port     = 443
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${local.name}-alb-sg"
    Environment = var.environment
    Project     = var.project
  }
}