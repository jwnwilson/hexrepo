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

data "aws_subnets" "private_subnet_ids" {
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


################################################################################
# RDS Module
################################################################################
# resource "random_password" "master"{
#   length           = 16
#   special          = true
#   override_special = "_!%^"
# }

# resource "aws_secretsmanager_secret" "password" {
#   name = "${var.project}-db-password"
# }

# resource "aws_secretsmanager_secret_version" "password" {
#   secret_id = aws_secretsmanager_secret.password.id
#   secret_string = random_password.master.result
# }

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 4"

  name        = "${var.project}-sg-${var.environment}"
  description = "Complete PostgreSQL example security group"
  vpc_id      = var.vpc_id

  # ingress
  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = data.aws_vpc.selected.cidr_block
    },
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = -1
      description = "PostgreSQL access from within VPC"
      cidr_blocks = var.vpc_cidr_block
    },
    {
      from_port   = 0
      to_port     = 0
      protocol    = -1
      description = "Allow all outgoing connections"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = module.db.db_instance_master_user_secret_arn
}

resource "aws_db_subnet_group" "default" {
  name       = "hexrepo-${var.environment}"
  subnet_ids = data.aws_subnets.private_subnet_ids.ids

  tags = {
    Name = "hexrepo-${var.environment}"
  }
}

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.10"

  identifier = "${var.project}-db-${var.environment}"

  create_db_option_group    = false
  create_db_parameter_group = true

  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    },
    {
      name  = "rds.force_ssl"
      value = 0
    },
    {
      name = "idle_in_transaction_session_timeout"
      value = 30000
    }
  ]

  # All available versions: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html#PostgreSQL.Concepts
  engine               = "postgres"
  engine_version       = "16"
  family               = "postgres16" # DB parameter group
  major_engine_version = "16"         # DB option group
  instance_class       = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100
  storage_encrypted     = false

  # NOTE: Do NOT use 'user' as the value for 'username' as it throws:
  # "Error creating DB Instance: InvalidParameterValue: MasterUsername
  # user cannot be used as it is a reserved word used by the engine"
  db_name                     = var.project
  username                    = var.username
  manage_master_user_password = true
  port                        = 5432

  multi_az               = false
  subnet_ids             = data.aws_subnets.private_subnet_ids.ids
  vpc_security_group_ids = [module.security_group.security_group_id]
  db_subnet_group_name   = aws_db_subnet_group.default.name

  tags = {
    Environment = terraform.workspace
    StartTime   = var.start_time
    StopTime    = var.stop_time
    Project     = var.project
  }

}
