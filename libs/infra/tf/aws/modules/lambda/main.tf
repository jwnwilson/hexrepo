# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

data "aws_vpc" "selected" {
  id = var.vpc_id
}

data "aws_subnets" "vpc_subnet_ids" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }

  tags = {
    Tier = "Private"
  }
}

data "aws_security_group" "selected" {
  vpc_id = data.aws_vpc.selected.id

  filter {
    name   = "group-name"
    values = ["default"]
  }
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4"

  name        = "${var.project}-sg-${var.environment}-internet-access"
  description = "Internet access for lambda"
  vpc_id      = var.vpc_id

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = -1
      description = "Allow all outgoing connections"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

module "lambda" {
  source                  = "terraform-aws-modules/lambda/aws"

  function_name           = "${var.project}_${var.environment}"
  description             = var.description

  create_package          = false

  image_uri               = "${var.ecr_url}:${var.docker_tag}"
  package_type            = "Image"
  architectures          = ["x86_64"]
  
  attach_network_policy   = true
  timeout                 = 30

  attach_tracing_policy   = true
  tracing_mode            = "Active"

  # This can be used to reduce the cold starts of lambda
  # provisioned_concurrent_executions = 10
  # publish                 = true

  environment_variables = merge(
    {
      ENVIRONMENT = var.environment
    },
    var.environment_variables,
  )

  image_config_command = var.lambda_command

  vpc_subnet_ids         = data.aws_subnets.vpc_subnet_ids.ids
  vpc_security_group_ids = concat(var.security_group_ids, [module.security_group.security_group_id])
}

# Schedule Lambda 

resource "aws_cloudwatch_event_rule" "schedule_lambda" {
  count               = var.lambda_schedule_expression ? 1 : 0
  name                = "every-one-minute"
  description         = "Fires every one minutes"
  # schedule_expression = "rate(1 minute)"
  schedule_expression = var.lambda_schedule_expression ? var.lambda_schedule_expression : null
}

resource "aws_cloudwatch_event_target" "check_foo_every_one_minute" {
  rule      = "${aws_cloudwatch_event_rule.every_one_minute.name}"
  target_id = "lambda"
  arn       = "${module.lambda.lambda_function_arn}"
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = "${module.lambda.lambda_function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.every_one_minute.arn}"
}

resource "aws_iam_policy" "sqs-secret-lambda-policy" {
  name        = "sqs-secret-lambda-policy-${var.project}-${var.environment}"
  description = "allow lambda access to sqs policy & secret manager"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "sqs:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Action": [
        "secretsmanager:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "sqs-attach" {
  role       = module.lambda.lambda_role_name
  policy_arn = aws_iam_policy.sqs-secret-lambda-policy.arn
}

