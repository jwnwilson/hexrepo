terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

locals {
  queue_name = "${var.project}_${var.environment}_${var.name}"
}

resource "aws_sqs_queue" "deadletter_queue" {
  name                        = "${local.queue_name}_deadletter"
  max_message_size            = 2048
  message_retention_seconds   = 86400
  receive_wait_time_seconds   = 10

  tags = {
    Environment = var.environment
  }
}

resource "aws_sqs_queue" "queue" {
  name                        = "${local.queue_name}"
  visibility_timeout_seconds  = 900
  max_message_size            = 2048
  message_retention_seconds   = 86400
  receive_wait_time_seconds   = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.deadletter_queue.arn
    maxReceiveCount     = 4
  })

  tags = {
    Environment = var.environment
  }
}
