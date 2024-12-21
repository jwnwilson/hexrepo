terraform {
  backend "s3" {
    region = "eu-west-1"
    bucket = "monorepo-jwn"
    key    = "monitor-environment.tfstate"
  }
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "monorepo" {
  filter {
    name   = "tag:Name"
    values = ["monorepo-vpc-${terraform.workspace}"]
  }
}

data "aws_security_group" "default_sg" {
  tags = {
    Name = "monorepo-vpc-${terraform.workspace}-default"
  }
}

data "aws_ecr_repository" "ecr_repo" {
  name = "monorepo-${var.project}"
}

resource "aws_iam_policy" "manage_ec2_rds" {
  name        = "manage_ec2_rds-${var.project}-${terraform.workspace}"
  description = "allow lambda access to manage ec2 and rds"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "ec2:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Action": [
        "rds:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "manage_ec2_rds_attach" {
  role       = module.monitor_lambda.lambda_role_name
  policy_arn = aws_iam_policy.manage_ec2_rds.arn
}

module "monitor_lambda" {
  source = "../../../../../../libs/infra/tf/aws/modules/lambda"

  environment                = terraform.workspace
  project                    = "monitor"
  ecr_url                    = data.aws_ecr_repository.ecr_repo.repository_url
  docker_tag                 = var.docker_tag
  vpc_id                     = data.aws_vpc.monorepo.id
  lambda_command             = ["src.app.interactor.event.aws.handler"]
  security_group_ids         = [data.aws_security_group.default_sg.id]
  lambda_schedule_expression = "cron(5 * * * ? *)"

  environment_variables = {
    ENVIRONMENT         = terraform.workspace
    CLOUD_PROVIDER      = "AWS"
    AWS_ACCOUNT         = "675468650888"
    AWS_TF_STATE_BUCKET = "monorepo-jwn"
  }
}
